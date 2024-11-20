#!/bin/sh
res=$1
echo bulk column ----
grep -P 'bulk\t' $res | grep TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 | cut -f6 
grep -P 'bulk\t' $res | grep TLS13_AES_256_GCM_SHA384 | head -2 | cut -f6 

echo
echo bulk unbuffered column ----
grep -P 'bulk-unbuffered\t' $res | grep TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 | cut -f6 
grep -P 'bulk-unbuffered\t' $res | grep TLS13_AES_256_GCM_SHA384 | head -2 | cut -f6 

echo
echo handshakes column ----
grep -P 'handshakes\t' $res | grep TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 | grep no-resume | cut -f8
grep -P 'handshakes\t' $res | grep TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 | grep no-resume | grep EcdsaP256 | cut -f8
grep -P 'handshakes\t' $res | grep TLS13_AES_256_GCM_SHA384 | grep no-resume | grep Rsa2048 | cut -f8
grep -P 'handshakes\t' $res | grep TLS13_AES_256_GCM_SHA384 | grep no-resume | grep EcdsaP256 | cut -f8

echo
echo handshakes unbuffered column ----
grep -P 'handshakes-unbuffered\t' $res | grep TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 | grep no-resume | cut -f8
grep -P 'handshakes-unbuffered\t' $res | grep TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 | grep no-resume | grep EcdsaP256 | cut -f8
grep -P 'handshakes-unbuffered\t' $res | grep TLS13_AES_256_GCM_SHA384 | grep Rsa2048 | grep no-resume | cut -f8
grep -P 'handshakes-unbuffered\t' $res | grep TLS13_AES_256_GCM_SHA384 | grep no-resume | grep EcdsaP256 | cut -f8

echo
echo resume column ----
grep -P 'handshakes\t' $res | grep TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 | grep sessionid | cut -f8
grep -P 'handshakes\t' $res | grep TLS13_AES_256_GCM_SHA384 | grep tickets | grep Rsa2048 | cut -f8

echo
echo resume unbuffered column ----
grep -P 'handshakes-unbuffered\t' $res | grep TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 | grep sessionid | cut -f8
grep -P 'handshakes-unbuffered\t' $res | grep TLS13_AES_256_GCM_SHA384| grep tickets | grep Rsa2048 | cut -f8
