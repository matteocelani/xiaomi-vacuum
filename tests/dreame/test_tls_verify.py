"""DreameTLSSocket checks the certificate chain, name, and handshake signature."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import Encoding
from custom_components.dreame_vacuum.dreame.protocol import (
    DreameVacuumDreameHomeCloudProtocol,
)
import pytest

_Socket = DreameVacuumDreameHomeCloudProtocol.DreameTLSSocket


def _name(common_name: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, common_name)])


def _signed(
    subject_key: rsa.RSAPrivateKey,
    issuer_key: rsa.RSAPrivateKey,
    subject: x509.Name,
    issuer: x509.Name,
    *,
    hostname: str | None,
    ca: bool,
    not_before: datetime | None = None,
    not_after: datetime | None = None,
) -> x509.Certificate:
    now = datetime.now(UTC)
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(subject_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before or now - timedelta(minutes=5))
        .not_valid_after(not_after or now + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
    )
    if hostname is not None:
        builder = builder.add_extension(
            x509.SubjectAlternativeName([x509.DNSName(hostname)]), critical=False
        )
    return builder.sign(issuer_key, hashes.SHA256())


def _chain(
    hostname: str = "mqtt.example",
) -> tuple[x509.Certificate, list[x509.Certificate]]:
    root_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    intermediate_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    root_name = _name("Test Root")
    intermediate_name = _name("Test Intermediate")
    root = _signed(root_key, root_key, root_name, root_name, hostname=None, ca=True)
    intermediate = _signed(
        intermediate_key, root_key, intermediate_name, root_name, hostname=None, ca=True
    )
    leaf = _signed(
        leaf_key,
        intermediate_key,
        _name(hostname),
        intermediate_name,
        hostname=hostname,
        ca=False,
    )
    return root, [leaf, intermediate]


def test_private_chain_accepts_a_named_leaf_and_rejects_the_wrong_name() -> None:
    root, chain = _chain()
    _Socket._verify_chain_to_root(chain, root, "mqtt.example")
    with pytest.raises(ValueError, match="hostname"):
        _Socket._verify_chain_to_root(chain, root, "other.example")


def test_private_chain_rejects_a_leaf_not_signed_by_the_issuer() -> None:
    root, chain = _chain()
    stranger = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    forged = _signed(
        stranger,
        stranger,
        _name("mqtt.example"),
        _name("Test Intermediate"),
        hostname="mqtt.example",
        ca=False,
    )
    with pytest.raises(ValueError):
        _Socket._verify_chain_to_root([forged, chain[1]], root, "mqtt.example")


def test_pinned_dreame_root_rejects_an_unrelated_chain() -> None:
    _root, chain = _chain()
    sock = _Socket("mqtt.example", 443, "mqtt.example", 1, None, private_ca=True)
    with pytest.raises(ValueError):
        sock._verify_private_chain(chain)


def test_public_store_rejects_a_private_leaf() -> None:
    _root, chain = _chain("api.example")
    der = chain[0].public_bytes(Encoding.DER)
    entries = len(der).to_bytes(3, "big") + der
    body = len(entries).to_bytes(3, "big") + entries
    sock = _Socket("api.example", 443, "api.example", 1, None, private_ca=False)
    with pytest.raises(ConnectionError, match="certificate verify failed"):
        sock._verify_chain(body, False)


def test_ca_without_key_cert_sign_is_rejected() -> None:
    root_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    bad_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    root_name = _name("Test Root")
    bad_name = _name("Not A Signer")
    root = _signed(root_key, root_key, root_name, root_name, hostname=None, ca=True)
    bad = (
        x509.CertificateBuilder()
        .subject_name(bad_name)
        .issuer_name(root_name)
        .public_key(bad_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC) - timedelta(minutes=5))
        .not_valid_after(datetime.now(UTC) + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(root_key, hashes.SHA256())
    )
    leaf = _signed(
        leaf_key,
        bad_key,
        _name("mqtt.example"),
        bad_name,
        hostname="mqtt.example",
        ca=False,
    )
    with pytest.raises(ValueError, match="keyCertSign"):
        _Socket._verify_chain_to_root([leaf, bad], root, "mqtt.example")


def test_tls12_downgrade_sentinel_is_rejected() -> None:
    sock = _Socket("mqtt.example", 443, "mqtt.example", 1, None)
    server_hello = bytes(6) + (b"\x00" * 24) + b"DOWNGRD" + b"\x01"
    with pytest.raises(ConnectionError, match="downgrade"):
        sock._handshake_tls12(b"", server_hello)


def test_handshake_signature_is_checked() -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    data = b"handshake"
    signature = key.sign(data, padding.PKCS1v15(), hashes.SHA256())
    _Socket._verify_signature(key.public_key(), 0x0401, signature, data)
    with pytest.raises(ConnectionError, match="signature"):
        _Socket._verify_signature(
            key.public_key(), 0x0401, signature[:-1] + b"\x00", data
        )
