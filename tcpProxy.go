package main

import (
	"bufio"
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
	"errors"
	"fmt"
	"github.com/joho/godotenv"
	"io"
	"io/ioutil"
	"log"
	"math"
	"net"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
)

type Proxy struct {
	iv  []byte
	key []byte
}

func NewProxy(key []byte, iv []byte) *Proxy {
	return &Proxy{
		iv:  iv,
		key: key,
	}
}

func (proxy *Proxy) decryptAES(cipherTextB64 string) (string, error) {
	cipherText, err := base64.StdEncoding.DecodeString(cipherTextB64)
	if err != nil {
		return "", err
	}

	block, err := aes.NewCipher(proxy.key)
	if err != nil {
		return "", err
	}

	if len(cipherText)%aes.BlockSize != 0 {
		return "", errors.New("cipherText non multiple de la taille de bloc")
	}

	mode := cipher.NewCBCDecrypter(block, proxy.iv)
	mode.CryptBlocks(cipherText, cipherText)

	padding := int(cipherText[len(cipherText)-1])
	if padding > aes.BlockSize || padding == 0 {
		return "", errors.New("padding invalide")
	}
	plainText := cipherText[:len(cipherText)-padding]

	return string(plainText), nil
}

func doHTTPRequest(method string, targetURL string) (int, string) {

	req, err := http.NewRequest(method, targetURL, nil)
	if err != nil {
		return 500, "FORGE_REQUEST_ERROR"
	}

	client := &http.Client{}

	resp, err := client.Do(req)
	if err != nil {
		return 500, "EXEC_REQUEST_ERROR"
	}
	defer func(Body io.ReadCloser) {
		err := Body.Close()
		if err != nil {
		}
	}(resp.Body)

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return 500, "READ_BODY_RESPONSE_ERROR"
	}

	return resp.StatusCode, string(body)
}

func pkcs7Pad(data []byte, blockSize int) []byte {
	padLen := blockSize - (len(data) % blockSize)
	if padLen == 0 {
		padLen = blockSize
	}
	pad := bytes.Repeat([]byte{byte(padLen)}, padLen)
	return append(data, pad...)
}

func (p *Proxy) encryptAESBase64(plainText string) (string, error) {
	block, err := aes.NewCipher(p.key)
	if err != nil {
		return "", err
	}
	if len(p.iv) != aes.BlockSize {
		return "", fmt.Errorf("IV doit faire %d octets", aes.BlockSize)
	}

	plain := pkcs7Pad([]byte(plainText), aes.BlockSize)

	cipherText := make([]byte, len(plain))
	mode := cipher.NewCBCEncrypter(block, p.iv)
	mode.CryptBlocks(cipherText, plain)

	return base64.StdEncoding.EncodeToString(cipherText), nil
}

func (proxy *Proxy) handleConnection(conn net.Conn) {
	defer func(conn net.Conn) {
		err := conn.Close()
		if err != nil {
		}
	}(conn)

	reader := bufio.NewReader(conn)
	msg, err := reader.ReadString('\n')
	if err != nil {
		log.Printf("Erreur lors de la lecture du message: %s\n", err.Error())
		return
	}
	msg = strings.TrimSpace(msg)

	decrypted, err := proxy.decryptAES(msg)
	if err != nil {
		log.Printf("Chiffrement invalide ! Erreur possible de déchiffrement: %s\n", err.Error())
		return
	}

	// Vérifier le format METHOD|timestamp|URL
	parts := strings.Split(decrypted, "|")
	if len(parts) != 3 {
		log.Println("Message invalide: mauvais format")
		_, err := conn.Write([]byte("Message invalide\n"))
		if err != nil {
			return
		}
		return
	}

	method := parts[0]
	timestampStr := parts[1]
	_url := parts[2]

	// Vérification méthode HTTP
	validMethods := map[string]bool{
		"GET": true, "POST": true, "PUT": true, "DELETE": true,
		"PATCH": true, "HEAD": true, "OPTIONS": true,
	}
	if !validMethods[method] {
		log.Printf("Méthode HTTP invalide: %s", method)
		_, err := conn.Write([]byte("Méthode HTTP invalide\n"))
		if err != nil {
			return
		}
		return
	}

	// Vérification timestamp
	ts, err := strconv.ParseInt(timestampStr, 10, 64)
	if err != nil {
		log.Printf("Timestamp invalide: %s", timestampStr)
		_, err := conn.Write([]byte("Timestamp invalide (conversion error)\n"))
		if err != nil {
			return
		}
		return
	}
	now := time.Now().Unix()
	if math.Abs(float64(ts-now)) > 60 {
		log.Printf("Timestamp trop ancien ou futur: %d", ts)
		_, err := conn.Write([]byte("Timestamp invalide (expired)\n"))
		if err != nil {
			return
		}
		return
	}

	_url = "http://localhost:9080" + _url
	_, err = url.Parse(_url)
	if err != nil {
		log.Printf("Erreur d'URL: %s", err.Error())
		_, err := conn.Write([]byte("Erreur d'URL\n"))
		if err != nil {
			return
		}
		return
	}

	log.Printf("| %s | Méthode: %s, Timestamp: %s, URL: %s", conn.RemoteAddr().String(), method, timestampStr, _url)

	statusCode, returnValue := doHTTPRequest(method, _url)

	response := strconv.Itoa(statusCode) + "|" + returnValue

	encodedResponse, err := proxy.encryptAESBase64(response)
	if err != nil {
		log.Printf("Erreur dans le chiffrement de la réponse: %s", err.Error())
		_, err := conn.Write([]byte("Erreur de chiffrement de la réponse !\n"))
		if err != nil {
			return
		}
		return
	}

	_, err = conn.Write([]byte(encodedResponse + "\n"))
	if err != nil {
		log.Printf("Erreur lors de l'envoi de la réponse: %s\n", err.Error())
	}
	return
}

func (proxy *Proxy) listen() {
	listener, err := net.Listen("tcp", "0.0.0.0:20821")
	if err != nil {
		log.Fatalf("Erreur lors de l'écoute sur 0.0.0.0:20821: %s\n", err.Error())
		return
	}
	log.Printf("Ecoute TCP sur %s", listener.Addr())
	for {
		conn, err := listener.Accept()
		if err != nil {
			log.Println("Erreur lors du handle de la connexion: " + err.Error())
			continue
		}
		go proxy.handleConnection(conn)
	}
}

func normalizeEnvVar(env string, length int) []byte {
	clean := strings.TrimSpace(env)
	if len(clean) > length {
		clean = clean[:length]
	} else if len(clean) < length {
		clean = clean + strings.Repeat("0", length-len(clean))
	}
	return []byte(clean)
}

func main() {

	err := godotenv.Load()
	if err != nil {
		log.Fatal("Erreur lors du chargement du fichier .env2")
	}

	key := normalizeEnvVar(os.Getenv("KEY"), 32)
	iv := normalizeEnvVar(os.Getenv("IV"), 16)

	if len(key) != 32 || len(iv) != 16 {
		log.Fatalf("Clé ou IV invalide: KEY=%d bytes, IV=%d bytes (il faut 16 chacun)", len(key), len(iv))
	}

	proxy := NewProxy(key, iv)
	go proxy.listen()

	select {} // Bloque le main
}
