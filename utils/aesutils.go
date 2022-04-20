package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"flag"
	"io"
	"io/ioutil"
	"log"
	"os"
	"github.com/rclone/rclone/lib/env"
)

func main() {
	// options
	var file, key string
	var encry, decry bool

	flag.StringVar(&file, "file", "", "the encrypt/decrypt file")
	flag.StringVar(&key, "key", "", "the key that encrypt/decrypt used")
	flag.BoolVar(&encry, "encry", false, "whether encrypt file or not")
	flag.BoolVar(&decry, "decry", false, "whether decrypt file or not")
	flag.Parse()

	if key == "" {
		fmt.Println("must set key option!")
		os.Exit(1)
	}

	if encry && decry {
		fmt.Println("only set encrypt or decrypt!")
		os.Exit(1)
	}

	if !encry && !decry {
		fmt.Println("must set encrypt or decrypt!")
		os.Exit(1)
	}

	text, err := ioutil.ReadFile(env.ShellExpand(file))
	if err != nil {
		fmt.Printf("error opening file(%s): %w\n", file, err)
		os.Exit(2)
	}

	if encry {
		ciphertext, err := encrypt(text, []byte(key))
		if err != nil {
			// TODO: Properly handle error
			log.Fatal(err)
		}
		fmt.Printf("%x\n", ciphertext)
	}

	if decry {
		ciphertext, _ := hex.DecodeString(string(text))
		plaintext, err := decrypt(ciphertext, []byte(key))
		if err != nil {
			// TODO: Properly handle error
			log.Fatal(err)
		}
		fmt.Printf("%s\n", plaintext)
	}
}

func encrypt(plaintext []byte, key []byte) ([]byte, error) {
	c, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}

	gcm, err := cipher.NewGCM(c)
	if err != nil {
		return nil, err
	}

	nonce := make([]byte, gcm.NonceSize())
	if _, err = io.ReadFull(rand.Reader, nonce); err != nil {
		return nil, err
	}

	return gcm.Seal(nonce, nonce, plaintext, nil), nil
}

func decrypt(ciphertext []byte, key []byte) ([]byte, error) {
	c, err := aes.NewCipher(key)
	if err != nil {
		fmt.Printf("1: %v", err)
		return nil, err
	}

	gcm, err := cipher.NewGCM(c)
	if err != nil {
		fmt.Printf("2: %v", err)
		return nil, err
	}

	nonceSize := gcm.NonceSize()
	if len(ciphertext) < nonceSize {
		return nil, errors.New("ciphertext too short")
	}

	nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]
	if err != nil {
		return nil, fmt.Errorf("plaintext error: %w", err)
	}

	return gcm.Open(nil, nonce, ciphertext, nil)
}
