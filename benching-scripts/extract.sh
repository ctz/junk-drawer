#!/bin/sh
echo bulk ----

echo transfer, 1.2, aes-128-gcm
grep -P 'bulk\t' result.txt | grep TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 | cut -f6 
echo transfer, 1.3, aes-256-gcm
grep -P 'bulk\t' result.txt | grep TLS13_AES_256_GCM_SHA384 | cut -f6 

echo transfer, 1.2, aes-128-gcm, unbuf
grep -P 'bulk-unbuffered\t' result.txt | grep TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 | cut -f6 
echo transfer, 1.3, aes-256-gcm, unbuf
grep -P 'bulk-unbuffered\t' result.txt | grep TLS13_AES_256_GCM_SHA384 | cut -f6 

echo
echo handshakes ----
echo full handshakes, 1.2, rsa
grep -P 'handshakes\t' result.txt | grep TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 | grep no-resume | cut -f8
echo resumed handshakes, 1.2
grep -P 'handshakes\t' result.txt | grep TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 | grep sessionid | cut -f8
echo full handshakes, 1.3, rsa
grep -P 'handshakes\t' result.txt | grep TLS13_AES_256_GCM_SHA384 | grep no-resume | cut -f8

echo full handshakes, 1.2, rsa, unbuf
grep -P 'handshakes-unbuffered\t' result.txt | grep TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 | grep no-resume | cut -f8
echo resumed handshakes, 1.2, unbuf
grep -P 'handshakes-unbuffered\t' result.txt | grep TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 | grep sessionid | cut -f8
echo full handshakes, 1.3, rsa, unbuf
grep -P 'handshakes-unbuffered\t' result.txt | grep TLS13_AES_256_GCM_SHA384 | grep no-resume | cut -f8
