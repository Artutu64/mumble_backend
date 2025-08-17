package main

import (
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
)

func main() {
	target := "http://127.0.0.1:9000"
	targetURL, err := url.Parse(target)
	if err != nil {
		log.Fatalf("Erreur parsing URL cible : %v", err)
	}

	proxy := httputil.NewSingleHostReverseProxy(targetURL)
	originalDirector := proxy.Director
	proxy.Director = func(req *http.Request) {
		originalDirector(req)
		req.Header.Set("X-Forwarded-Host", req.Host)
		req.Header.Set("X-Forwarded-Proto", "https")
		req.Host = targetURL.Host
	}

	httpsEnv := os.Getenv("HTTPS")
	certFile := os.Getenv("Certificat")
	if certFile == "" {
		certFile = "./none.crt"
	}
	keyFile := "key.pem"

	useHTTPS := false

	if httpsEnv == "True" || httpsEnv == "true" || httpsEnv == "1" {
		if _, err := os.Stat(certFile); os.IsNotExist(err) {
			log.Println("Certificat introuvable, démarrage en HTTP uniquement")
		} else if _, err := os.Stat(keyFile); os.IsNotExist(err) {
			log.Println("Clé introuvable, démarrage en HTTP uniquement")
		} else {
			useHTTPS = true
		}
	}

	if useHTTPS {
		go func() {
			log.Println("Reverse proxy HTTPS démarré sur :443")
			err := http.ListenAndServeTLS(":443", certFile, keyFile, proxy)
			if err != nil {
				log.Fatalf("Erreur serveur HTTPS : %v", err)
			}
		}()

		go func() {
			log.Println("Serveur HTTP redirection 80 démarré")
			err := http.ListenAndServe(":80", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				http.Redirect(w, r, "https://"+r.Host+r.RequestURI, http.StatusMovedPermanently)
			}))
			if err != nil {
				log.Fatalf("Erreur serveur HTTP : %v", err)
			}
		}()

	} else {
		log.Println("Proxy démarré en HTTP seul sur :80")
		err := http.ListenAndServe(":80", proxy)
		if err != nil {
			log.Fatalf("Erreur serveur HTTP : %v", err)
		}
	}

	select {}
}
