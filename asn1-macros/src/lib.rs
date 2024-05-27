use core::fmt::Debug;
use core::mem;

macro_rules! asn1_struct_ty(
    (INTEGER) => { Integer<'a> };
    (OBJECT IDENTIFIER) => { ObjectId };
    (ANY OPTIONAL) => { Option<Any<'a>> };
    (OCTET STRING) => { OctetString<'a> };
    ($ty:tt REF) => { $ty<'a> };
    ($ty:tt) => { $ty };
);

macro_rules! asn1_struct_parse_ty(
    ($p:ident, INTEGER) => { Integer::parse(&mut $p)? };
    ($p:ident, OBJECT IDENTIFIER) => { ObjectId::parse(&mut $p)? };
    ($p:ident, ANY OPTIONAL) => { Option::<Any>::parse(&mut $p)? };
    ($p:ident, OCTET STRING) => { OctetString::parse(&mut $p)? };
    ($p:ident, $ty:tt REF) => { $ty::parse(&mut $p)? };
    ($p:ident, $ty:tt) => { $ty::parse(&mut $p)? };
);

macro_rules! asn1_struct {
    ($name:ident ::= SEQUENCE { $($itname:ident $itty:ident $($opt:ident)? ),+ }) => {
        #[allow(non_snake_case)]
        #[derive(Clone, Debug)]
        pub struct $name<'a> {
            $( pub $itname: asn1_struct_ty!($itty $($opt)?), )+
        }

        impl<'a> $name<'a> {
            pub fn body_len(&self) -> usize {
                let mut result = 0;
                $( result += dbg!(self.$itname.encoded_len()); )+
                result
            }
        }

        impl<'a> Type<'a> for $name<'a> {
            fn parse(parser: &mut Parser<'a>) -> Result<Self, Error> {
                let (_, mut sub) = parser.descend(Tag::sequence())?;
                Ok(Self {
                $( $itname: asn1_struct_parse_ty!(sub, $itty $($opt)?), )+
                })
            }

            fn encoded_len(&self) -> usize {
                encoded_length_for(self.body_len())
            }

            fn encode(&self, encoder: &mut Encoder<'_>) -> Result<usize, Error> {
                let mut body = encoder.begin(Tag::sequence(), self.body_len())?;
                $( self.$itname.encode(&mut body)?; )+
                Ok(body.finish())
            }
        }
    }
}

macro_rules! asn1_enum {
    ($name:ident ::= INTEGER { $( $vname:ident($num:expr) ),+ }) => {
        #[allow(non_camel_case_types)]
        #[derive(Copy, Clone, Debug)]
        pub enum $name {
            $( $vname = $num, )+
        }

        impl Type<'_> for $name {
            fn parse(p: &mut Parser<'_>) -> Result<Self, Error> {
                match Integer::parse(p).and_then(|i| i.as_usize())? {
                    $( $num => Ok(Self::$vname), )+
                    _ => Err(Error::UnhandledEnumValue),
                }
            }

            fn encode(&self, encoder: &mut Encoder<'_>) -> Result<usize, Error> {
                let value = *self as usize;
                let bytes = value.to_be_bytes();
                Integer::from_bytes(&bytes).encode(encoder)
            }

            fn encoded_len(&self) -> usize {
                let byte_len = match (*self as usize) {
                    0..=0x7f => 1,
                    0x80..=0x7fff => 2,
                    0x8000..=0x7fffff => 3,
                    0x800000..=0x7fffffff => 4,
                    _ => todo!(),
                };
                encoded_length_for(byte_len)
            }
        }
    }
}

macro_rules! asn1_oid_indices {
    ([$($accum:tt)*] -> ) => { [ $($accum,)* ] };
    ([$($accum:tt)*] -> $name:ident ($val:literal) $($rest:tt)*) => { asn1_oid_indices!([$($accum)* $val] -> $($rest)*) };
    ([$($accum:tt)*] -> $val:literal $($rest:tt)*) => { asn1_oid_indices!([$($accum)* $val] ->  $($rest)*) };
}

macro_rules! asn1_oid {
    ($name:ident OBJECT IDENTIFIER ::= { $( $item:tt )+ }) => {
        pub static $name: ObjectId = ObjectId::from_path(&asn1_oid_indices!( [] -> $( $item )+));
    }
}

asn1_struct! {
    RSAPublicKey ::= SEQUENCE {
        modulus           INTEGER,
        publicExponent    INTEGER
    }
}

asn1_struct! {
    RSAPrivateKey ::= SEQUENCE {
        version           Version,
        modulus           INTEGER,
        publicExponent    INTEGER,
        privateExponent   INTEGER,
        prime1            INTEGER,
        prime2            INTEGER,
        exponent1         INTEGER,
        exponent2         INTEGER,
        coefficient       INTEGER
    }
}

asn1_enum! {
    Version ::= INTEGER { two_prime(0), multi(1) }
}

asn1_oid! {
    id_md5      OBJECT IDENTIFIER ::= {
           iso (1) member_body (2) us (840) rsadsi (113549)
           digestAlgorithm (2) 5
    }
}

asn1_oid! {
    id_ecPublicKey OBJECT IDENTIFIER ::= {
        iso(1) member_body(2) us(840) 10045 keyType(2) 1
    }
}

asn1_oid! {
    id_prime256v1 OBJECT IDENTIFIER ::= {
        iso(1) member_body(2) us(840) 10045 curves(3) prime(1) 7
    }
}

asn1_struct! {
    PrivateKeyInfo ::= SEQUENCE {
        version                   INTEGER,
        privateKeyAlgorithm       AlgorithmIdentifier REF,
        privateKey                OCTET STRING
    }
}

asn1_struct! {
    AlgorithmIdentifier ::= SEQUENCE {
        algorithm                 OBJECT IDENTIFIER,
        parameters                ANY OPTIONAL
    }
}

asn1_struct! {
    EcPrivateKey ::= SEQUENCE {
        version                   EcPrivateKeyVer,
        privateKey                OCTET STRING
    }
}

asn1_enum! {
    EcPrivateKeyVer ::= INTEGER { ecPrivkeyVer1(1) }
}

pub trait Type<'a>: Debug + Sized {
    fn parse(p: &mut Parser<'a>) -> Result<Self, Error>;
    fn encode(&self, encoder: &mut Encoder<'_>) -> Result<usize, Error>;
    fn encoded_len(&self) -> usize;
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Any<'a> {
    Null(Null),
    Integer(Integer<'a>),
    OctetString(OctetString<'a>),
    ObjectId(ObjectId),
}

impl<'a> Type<'a> for Any<'a> {
    fn parse(p: &mut Parser<'a>) -> Result<Self, Error> {
        match dbg!(p.peek_tag()?.0) {
            Tag::NULL => Ok(Self::Null(Null::parse(p)?)),
            Tag::INTEGER => Ok(Self::Integer(Integer::parse(p)?)),
            Tag::OCTET_STRING => Ok(Self::OctetString(OctetString::parse(p)?)),
            Tag::OBJECT_ID => Ok(Self::ObjectId(ObjectId::parse(p)?)),
            _ => Err(Error::UnexpectedTag),
        }
    }

    fn encode(&self, encoder: &mut Encoder<'_>) -> Result<usize, Error> {
        match self {
            Self::Null(n) => n.encode(encoder),
            Self::Integer(i) => i.encode(encoder),
            Self::OctetString(os) => os.encode(encoder),
            Self::ObjectId(obj) => obj.encode(encoder),
        }
    }

    fn encoded_len(&self) -> usize {
        match self {
            Self::Null(n) => n.encoded_len(),
            Self::Integer(i) => i.encoded_len(),
            Self::OctetString(os) => os.encoded_len(),
            Self::ObjectId(obj) => obj.encoded_len(),
        }
    }
}

impl<'a> Type<'a> for Option<Any<'a>> {
    fn parse(p: &mut Parser<'a>) -> Result<Self, Error> {
        if p.left() > 0 {
            Any::parse(p).map(Some)
        } else {
            Ok(None)
        }
    }

    fn encode(&self, encoder: &mut Encoder<'_>) -> Result<usize, Error> {
        match self {
            None => Ok(0),
            Some(a) => a.encode(encoder),
        }
    }

    fn encoded_len(&self) -> usize {
        match self {
            None => 0,
            Some(a) => a.encoded_len(),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Null;

impl Type<'_> for Null {
    fn parse(p: &mut Parser<'_>) -> Result<Self, Error> {
        let (_, body) = p.take(Tag::null())?;
        if !body.is_empty() {
            return Err(Error::IllegalNull);
        }
        Ok(Self)
    }

    fn encode(&self, encoder: &mut Encoder<'_>) -> Result<usize, Error> {
        Ok(encoder.begin(Tag::null(), 0)?.finish())
    }

    fn encoded_len(&self) -> usize {
        encoded_length_for(0)
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ObjectId {
    buf: [u8; Self::MAX_LEN],
    used: usize,
}

impl ObjectId {
    const fn from_path(path: &[usize]) -> ObjectId {
        let mut r = ObjectId {
            buf: [0u8; Self::MAX_LEN],
            used: 0,
        };

        match path.len() {
            0 => {}
            1 => {
                r.buf[r.used] = path[0] as u8;
                r.used += 1;
            }
            2.. => {
                r.buf[r.used] = (path[0] as u8) * 40 + (path[1] as u8);
                r.used += 1;

                let mut i = 2;
                loop {
                    if i == path.len() {
                        break;
                    }
                    let item = path[i];
                    i += 1;

                    if item < 0x7f {
                        r.buf[r.used] = item as u8;
                        r.used += 1;
                    } else {
                        let mut chunks = (item.ilog2() + 6) / 7;

                        while chunks > 1 {
                            chunks -= 1;
                            r.buf[r.used] = (item >> (chunks * 7)) as u8 | 0x80u8;
                            r.used += 1;
                        }

                        r.buf[r.used] = (item & 0x7f) as u8;
                        r.used += 1;
                    }
                }
            }
        }

        r
    }

    const MAX_LEN: usize = 16;
}

impl Type<'_> for ObjectId {
    fn parse(p: &mut Parser<'_>) -> Result<Self, Error> {
        let (_, body) = p.take(Tag::object_id())?;
        if body.len() > Self::MAX_LEN {
            return Err(Error::UnsupportedLargeObjectId);
        }

        let mut buf = [0u8; Self::MAX_LEN];
        buf[..body.len()].copy_from_slice(body);
        Ok(Self {
            buf,
            used: body.len(),
        })
    }

    fn encode(&self, encoder: &mut Encoder<'_>) -> Result<usize, Error> {
        let mut body = encoder.begin(Tag::object_id(), self.used)?;
        body.append_slice(self.as_ref())?;
        Ok(body.finish())
    }

    fn encoded_len(&self) -> usize {
        encoded_length_for(self.used)
    }
}

impl AsRef<[u8]> for ObjectId {
    fn as_ref(&self) -> &[u8] {
        &self.buf[..self.used]
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Integer<'a> {
    twos_complement: &'a [u8],
}

impl<'a> Integer<'a> {
    fn from_bytes(mut bytes: &'a [u8]) -> Self {
        static ZERO: &[u8] = &[0];

        dbg!(bytes);
        if bytes.is_empty() || bytes.iter().all(|b| *b == 0x00) {
            return Integer {
                twos_complement: ZERO,
            };
        }

        let negative = dbg!(bytes[0] & 0x80 == 0x80);

        if negative {
            while bytes.len() > 1 && bytes[0] == 0xff && bytes[1] & 0x80 == 0x80 {
                bytes = &bytes[1..];
            }
        } else {
            while bytes.len() > 1 && bytes[0] == 0x00 && bytes[1] & 0x80 == 0x00 {
                bytes = &bytes[1..];
            }
        }

        Integer {
            twos_complement: bytes,
        }
    }

    fn is_negative(&self) -> bool {
        self.twos_complement
            .first()
            .map(|b| b & 0x80 == 0x80)
            .unwrap_or_default()
    }

    fn as_usize(&self) -> Result<usize, Error> {
        if self.is_negative() || self.twos_complement.len() > mem::size_of::<usize>() {
            return Err(Error::IntegerOutOfRange);
        }

        let mut bytes = [0u8; 8];
        for (i, b) in self.twos_complement.iter().enumerate() {
            bytes[bytes.len() - 1 - i] = *b;
        }
        Ok(usize::from_be_bytes(bytes))
    }
}

impl<'a> Type<'a> for Integer<'a> {
    fn parse(p: &mut Parser<'a>) -> Result<Self, Error> {
        let (_, twos_complement) = p.take(Tag::integer())?;
        Ok(Self { twos_complement })
    }

    fn encode(&self, encoder: &mut Encoder<'_>) -> Result<usize, Error> {
        let mut body = encoder.begin(Tag::integer(), self.twos_complement.len())?;
        body.append_slice(self.twos_complement)?;
        Ok(body.finish())
    }

    fn encoded_len(&self) -> usize {
        encoded_length_for(self.twos_complement.len())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct OctetString<'a> {
    octets: &'a [u8],
}

impl<'a> Type<'a> for OctetString<'a> {
    fn parse(p: &mut Parser<'a>) -> Result<Self, Error> {
        let (_, octets) = p.take(Tag::octet_string())?;
        Ok(Self { octets })
    }

    fn encode(&self, encoder: &mut Encoder<'_>) -> Result<usize, Error> {
        let mut body = encoder.begin(Tag::octet_string(), self.octets.len())?;
        body.append_slice(self.octets)?;
        Ok(body.finish())
    }

    fn encoded_len(&self) -> usize {
        encoded_length_for(self.octets.len())
    }
}

pub struct Parser<'a> {
    input: &'a [u8],
}

impl<'a, 's> Parser<'a> {
    pub fn new(buf: &'a [u8]) -> Self {
        Self { input: buf }
    }

    fn take(&'s mut self, want_tag: Tag) -> Result<(Tag, &'a [u8]), Error> {
        let tag = self.one_byte()?;
        dbg!((want_tag, tag));
        if !want_tag.acceptable(tag) {
            return Err(Error::UnexpectedTag);
        }

        let len = self.take_len()?;
        let body = self.input.get(..len).ok_or(Error::UnexpectedEof)?;
        let (_, rest) = self.input.split_at(len);
        self.input = rest;
        Ok((Tag::from(tag), body))
    }

    fn descend(&'s mut self, want_tag: Tag) -> Result<(Tag, Parser<'a>), Error> {
        let (tag, body) = self.take(want_tag)?;
        Ok((tag, Parser::new(body)))
    }

    fn peek_tag(&'s mut self) -> Result<Tag, Error> {
        self.input
            .get(0)
            .cloned()
            .map(Tag)
            .ok_or(Error::UnexpectedEof)
    }

    fn left(&self) -> usize {
        self.input.len()
    }

    #[inline]
    fn one_byte(&'s mut self) -> Result<u8, Error> {
        let (byte, rest) = self.input.split_first().ok_or(Error::UnexpectedEof)?;
        self.input = rest;
        Ok(*byte)
    }

    fn take_len(&'s mut self) -> Result<usize, Error> {
        let len_byte = self.one_byte()?;

        match dbg!(len_byte) {
            0x00..=0x7f => Ok(len_byte as usize),
            0x81 => {
                let len = self.one_byte()?;
                if len < 0x80 {
                    return Err(Error::NonCanonicalEncoding);
                }
                Ok(len as usize)
            }
            0x82 => {
                let len = ((self.one_byte()? as usize) << 8) | self.one_byte()? as usize;
                if len < 0xff {
                    return Err(Error::NonCanonicalEncoding);
                }
                Ok(len)
            }
            _ => todo!(),
        }
    }
}

pub struct Encoder<'a> {
    out: &'a mut [u8],
    written: usize,
}

impl<'a, 's> Encoder<'a> {
    pub fn new(out: &'a mut [u8]) -> Self {
        Encoder { out, written: 0 }
    }

    fn push(&'s mut self, byte: u8) -> Result<(), Error> {
        if self.out.len() < 1 {
            return Err(Error::UnexpectedEof);
        }
        let out = mem::take(&mut self.out);
        out[0] = byte;
        self.out = &mut out[1..];
        self.written += 1;
        Ok(())
    }

    fn append_slice(&'s mut self, bytes: &[u8]) -> Result<(), Error> {
        if self.out.len() < bytes.len() {
            return Err(Error::UnexpectedEof);
        }

        let out = mem::take(&mut self.out);
        out[..bytes.len()].copy_from_slice(bytes);
        self.out = &mut out[bytes.len()..];
        self.written += bytes.len();
        Ok(())
    }

    fn split(&'s mut self, len: usize) -> Result<Encoder<'a>, Error> {
        if self.out.len() < len {
            return Err(Error::UnexpectedEof);
        }

        let buffer = mem::take(&mut self.out);
        let (split, rest) = buffer.split_at_mut(len);
        self.out = rest;
        let before = self.written;
        self.written += len;
        Ok(Encoder {
            out: split,
            written: before,
        })
    }

    pub fn begin(&'s mut self, tag: Tag, body_len: usize) -> Result<Encoder<'a>, Error> {
        self.push(tag.0)?;

        match body_len {
            0..=0x7f => self.push(body_len as u8)?,
            0x80.. => {
                let bytes = ((body_len.ilog2() + 7) / 8) as usize;
                self.push(0x80 + bytes as u8)?;
                let len_encoded = body_len.to_be_bytes();
                for i in 0..bytes {
                    self.push(len_encoded[len_encoded.len() - bytes + i])?;
                }
            }
        }

        self.split(body_len)
    }

    pub fn finish(&mut self) -> usize {
        self.written
    }
}

fn encoded_length_for(len: usize) -> usize {
    const TAG: usize = 1;
    match len {
        0..=0x7f => TAG + 1 + len,
        0x80..=0xff => TAG + 1 + 1 + len,
        0x01_00..=0xff_ff => TAG + 1 + 2 + len,
        0x01_00_00..=0xff_ff_ff => TAG + 1 + 3 + len,
        0x01_00_00_00..=0xff_ff_ff_ff => TAG + 1 + 4 + len,
        _ => todo!(),
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Error {
    UnexpectedTag,
    UnexpectedEof,
    NonCanonicalEncoding,
    UnhandledEnumValue,
    IntegerOutOfRange,
    IllegalNull,
    UnsupportedLargeObjectId,
    NyiTodo,
}

#[derive(Clone, Copy, Debug)]
pub struct Tag(u8);

impl Tag {
    fn acceptable(&self, offered: u8) -> bool {
        self.0 == offered
    }

    fn sequence() -> Self {
        Self(0x30)
    }

    fn integer() -> Self {
        Self(Self::INTEGER)
    }

    fn octet_string() -> Self {
        Self(Self::OCTET_STRING)
    }

    fn null() -> Self {
        Self(Self::NULL)
    }

    fn object_id() -> Self {
        Self(Self::OBJECT_ID)
    }

    const INTEGER: u8 = 0x02;
    const OCTET_STRING: u8 = 0x04;
    const NULL: u8 = 0x05;
    const OBJECT_ID: u8 = 0x06;
}

impl From<u8> for Tag {
    fn from(b: u8) -> Self {
        Self(b)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        println!("{:x?}", id_md5.as_ref());
    }

    #[test]
    fn test_integer_encoding() {
        check_integer_from_bytes(&[0u8; 16], &[0x02, 0x01, 0x00]);
        check_integer_from_bytes(&[], &[0x02, 0x01, 0x00]);
        check_integer_from_isize(0, &[0x02, 0x01, 0x00]);

        // negative sign contraction
        check_integer_from_bytes(&[0xffu8; 32], &[0x02, 0x01, 0xff]);
        check_integer_from_bytes(&[0xff, 0xff, 0x01], &[0x02, 0x02, 0xff, 0x01]);
        check_integer_from_isize(-1, &[0x02, 0x01, 0xff]);
        check_integer_from_isize(-127, &[0x02, 0x01, 0x81]);

        // positive zero constraction
        check_integer_from_bytes(&[0x00, 0x00, 0x80], &[0x02, 0x02, 0x00, 0x80]);
        check_integer_from_bytes(&[0x00, 0x00, 0x7f], &[0x02, 0x01, 0x7f]);
        check_integer_from_isize(128, &[0x02, 0x02, 0x00, 0x80]);
        check_integer_from_isize(127, &[0x02, 0x01, 0x7f]);
    }

    fn check_integer_from_bytes(bytes: &[u8], encoding: &[u8]) {
        let mut buf = vec![0u8; encoding.len()];
        let len = Integer::from_bytes(bytes)
            .encode(&mut Encoder::new(&mut buf))
            .unwrap();
        buf.truncate(len);
        assert_eq!(&buf, encoding);
    }

    fn check_integer_from_isize(num: isize, encoding: &[u8]) {
        let mut buf = vec![0u8; encoding.len()];
        let len = Integer::from_bytes(&num.to_be_bytes())
            .encode(&mut Encoder::new(&mut buf))
            .unwrap();
        buf.truncate(len);
        assert_eq!(&buf, encoding);
    }

    #[test]
    fn parse_public_key() {
        let data = include_bytes!("testdata/rsapublickey-1k.bin");
        let key = RSAPublicKey::parse(&mut Parser::new(data)).unwrap();
        dbg!(&key);

        dbg!(data.len());
        assert_eq!(key.encoded_len(), data.len());

        let mut buf = [0u8; 256];
        let encode_len = key.encode(&mut Encoder::new(&mut buf)).unwrap();
        dbg!(encode_len);
        println!("{:?}", &buf[..encode_len]);
        assert_eq!(data, &buf[..encode_len]);
    }

    #[test]
    fn parse_private_key() {
        let data = include_bytes!("testdata/rsaprivatekey-1k.bin");
        let key = RSAPrivateKey::parse(&mut Parser::new(data)).unwrap();
        dbg!(&key);

        dbg!(data.len());
        assert_eq!(key.encoded_len(), data.len());
    }

    #[test]
    fn parse_pkcs8_key() {
        let data = include_bytes!("testdata/nistp256-p8.bin");
        let key = PrivateKeyInfo::parse(&mut Parser::new(data)).unwrap();
        dbg!(&key);
        assert_eq!(key.version, Integer::from_bytes(&[0]));
        assert_eq!(key.privateKeyAlgorithm.algorithm, id_ecPublicKey);
        assert_eq!(
            key.privateKeyAlgorithm.parameters,
            Some(Any::ObjectId(id_prime256v1.clone()))
        );

        let inner = EcPrivateKey::parse(&mut Parser::new(key.privateKey.octets)).unwrap();
        dbg!(&inner);
    }

    #[test]
    fn parse_sec1_key() {
        let data = include_bytes!("testdata/nistp256-sec1.bin");
        let key = EcPrivateKey::parse(&mut Parser::new(data)).unwrap();
        dbg!(&key);
    }
}
