from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import datetime
from datetime import timezone

# Generate a private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Define subject and issuer
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"State"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"City"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Organization"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),  # Change to your domain name if needed
])

# Create a self-signed certificate
cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    private_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.now(timezone.utc)
).not_valid_after(
    # Valid for 1 year
    datetime.datetime.now(timezone.utc) + datetime.timedelta(days=365)
).sign(private_key, hashes.SHA256(), default_backend())

# Save the private key to a file
with open("key.pem", "wb") as key_file:
    key_file.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Save the certificate to a file
with open("cert.pem", "wb") as cert_file:
    cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
