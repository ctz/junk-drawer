#!/bin/sh

file=$1
python table.py $file \
         'tls1.2 rsa server ticket resumptions=handshakes TLSv1_2 Rsa2048 TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 server server-auth tickets' \
         'tls1.2 rsa server stateful resumptions=handshakes TLSv1_2 Rsa2048 TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 server server-auth sessionid' \
         'tls1.3 rsa server resumptions=handshakes TLSv1_3 Rsa2048 TLS13_AES_256_GCM_SHA384 server server-auth tickets'

echo tls1.2 rsa client full
python slice.py $file handshakes TLSv1_2 Rsa2048 TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 client server-auth no-resume
echo tls1.2 rsa server full
python slice.py $file handshakes TLSv1_2 Rsa2048 TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 server server-auth no-resume

echo tls1.2 rsa client ticket resumptions
python slice.py $file handshakes TLSv1_2 Rsa2048 TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 client server-auth tickets
echo tls1.2 rsa server ticket resumptions
python slice.py $file handshakes TLSv1_2 Rsa2048 TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 server server-auth tickets

echo tls1.2 rsa client stateful resumptions
python slice.py $file handshakes TLSv1_2 Rsa2048 TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 client server-auth sessionid
echo tls1.2 rsa server stateful resumptions
python slice.py $file handshakes TLSv1_2 Rsa2048 TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 server server-auth sessionid

echo tls1.3 rsa client full
python slice.py $file handshakes TLSv1_3 Rsa2048 TLS13_AES_256_GCM_SHA384 client server-auth no-resume
echo tls1.3 rsa server full
python slice.py $file handshakes TLSv1_3 Rsa2048 TLS13_AES_256_GCM_SHA384 server server-auth no-resume

echo tls1.3 rsa client resumptions
python slice.py $file handshakes TLSv1_3 Rsa2048 TLS13_AES_256_GCM_SHA384 client server-auth tickets
echo tls1.3 rsa server resumptions
python slice.py $file handshakes TLSv1_3 Rsa2048 TLS13_AES_256_GCM_SHA384 server server-auth tickets


