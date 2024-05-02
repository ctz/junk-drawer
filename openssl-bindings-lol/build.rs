use std::env;
use std::path::PathBuf;
use std::process::Command;

fn main() {
    println!("cargo:rerun-if-changed=build/wrapper.h");

    Command::new("./Configure")
        .current_dir("openssl/")
        .spawn()
        .expect("cannot configure openssl");

    Command::new("make")
        .arg("build_generated")
        .current_dir("openssl/")
        .spawn()
        .expect("cannot generate openssl header files (requires Perl 5.10)");

    println!("cargo:rerun-if-changed=openssl/include/openssl/ssl.h");

    let bindings = bindgen::Builder::default()
        .clang_arg("-Iopenssl/include")
        .header("build/wrapper.h")
        .parse_callbacks(Box::new(bindgen::CargoCallbacks))
        .generate()
        .expect("Unable to generate bindings");

    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("entry.rs"))
        .expect("Couldn't write entrypoints!");
}
