use serde_json::Value;
use reqwest::Client;
use std::time::Duration;

pub const PREFERRED_MODELS: &[&str] = &[
    "magicworld-gm",
    "magicworld-gm:latest",
    "llama3.2:3b",
    "llama3.2:3b:latest",
    "qwen2.5:1.5b",
    "qwen2.5:latest",
    "llama3.2:1b",
    "llama3.2:latest",
];

#[derive(Clone)]
pub struct OllamaClient {
    pub provider: String,
    pub host: String,
    pub default_model: String,
    pub api_key: Option<String>,
    client: Client,
}

impl OllamaClient {
    pub async fn new() -> Self {
        // Read configuration (can default to direct Ollama)
        let provider = std::env::var("LLM_PROVIDER").unwrap_or_else(|_| "ollama".to_string());
        let host = std::env::var("LLM_HOST").unwrap_or_else(|_| "http://127.0.0.1:11434".to_string());
        let default_model = std::env::var("LLM_MODEL").unwrap_or_else(|_| "magicworld-gm".to_string());
        let api_key = std::env::var("LLM_API_KEY").ok();

        let client = Client::builder()
            .timeout(Duration::from_secs(300))
            .no_proxy()
            .build()
            .unwrap_or_default();

        let mut self_client = OllamaClient {
            provider,
            host,
            default_model,
            api_key,
            client,
        };

        if self_client.provider == "ollama" {
            self_client.auto_detect_model().await;
        }

        self_client
    }

    async fn auto_detect_model(&mut self) {
        let url = format!("{}/api/tags", self.host);
        if let Ok(res) = self.client.get(&url).send().await {
            if res.status().is_success() {
                if let Ok(val) = res.json::<Value>().await {
                    if let Some(models) = val["models"].as_array() {
                        let model_names: Vec<&str> = models
                            .iter()
                            .filter_map(|m| m["name"].as_str())
                            .collect();

                        let mut selected = None;
                        for preferred in PREFERRED_MODELS {
                            for name in &model_names {
                                if *name == *preferred || name.starts_with(&format!("{}:", preferred.split(':').next().unwrap())) {
                                    selected = Some((*name).to_string());
                                    break;
                                }
                            }
                            if selected.is_some() {
                                break;
                            }
                        }

                        if let Some(sel) = selected {
                            self.default_model = sel;
                            println!("[Ollama] Active model auto-detected: '{}'", self.default_model);
                        } else if !model_names.is_empty() {
                            self.default_model = model_names[0].to_string();
                            println!("[Ollama] No preferred model found. Using fallback: '{}'", self.default_model);
                        }
                    }
                }
            }
        }
    }

    pub async fn is_available(&self) -> bool {
        if self.provider == "groq" || self.provider == "openai" {
            return true;
        }
        let url = if self.provider == "ollama" {
            format!("{}/api/tags", self.host)
        } else {
            self.host.clone()
        };

        match self.client.get(&url).timeout(Duration::from_secs(2)).send().await {
            Ok(res) => res.status().is_success(),
            Err(_) => false,
        }
    }

    pub async fn generate_chat(&self, messages: &[Value], model: Option<&str>) -> String {
        let model_name = model.unwrap_or(&self.default_model);

        if self.provider == "odysseus" || self.provider == "openai_compatible" || self.provider == "groq" || self.provider == "openai" {
            let mut host_url = self.host.clone();
            if self.provider == "groq" && (host_url.contains("127.0.0.1") || host_url.contains("localhost") || host_url.contains("ollama")) {
                host_url = "https://api.groq.com/openai/v1".to_string();
            } else if self.provider == "openai" && (host_url.contains("127.0.0.1") || host_url.contains("localhost") || host_url.contains("ollama")) {
                host_url = "https://api.openai.com/v1".to_string();
            }
            let url = format!("{}/chat/completions", host_url.trim_end_matches('/'));
            let mut req = self.client.post(&url).header("Content-Type", "application/json");
            
            let api_key = if self.provider == "openai" {
                self.api_key.clone().or_else(|| std::env::var("OPENAI_API_KEY").ok())
            } else {
                self.api_key.clone().or_else(|| std::env::var("GROQ_API_KEY").ok())
            };
            if let Some(ref key) = api_key {
                req = req.header("Authorization", format!("Bearer {}", key));
            }

            let payload = serde_json::json!({
                "model": model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 512
            });

            match req.json(&payload).send().await {
                Ok(res) if res.status().is_success() => {
                    if let Ok(data) = res.json::<Value>().await {
                        if let Some(content) = data["choices"][0]["message"]["content"].as_str() {
                            return content.trim().to_string();
                        }
                    }
                    String::new()
                }
                Ok(res) => format!("[Error de conexión con {}: {}]", self.provider, res.status()),
                Err(e) => {
                    eprintln!("[{}] Connection error: {}", self.provider, e);
                    format!("El Dungeon Master necesita un momento para recomponerse... ({} no disponible)", self.provider)
                }
            }
        } else {
            let url = format!("{}/api/chat", self.host);
            let payload = serde_json::json!({
                "model": model_name,
                "messages": messages,
                "stream": false,
                "keep_alive": "10m",
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                    "num_predict": 512
                }
            });

            match self.client.post(&url).json(&payload).send().await {
                Ok(res) if res.status().is_success() => {
                    if let Ok(data) = res.json::<Value>().await {
                        if let Some(content) = data["message"]["content"].as_str() {
                            return content.trim().to_string();
                        }
                    }
                    String::new()
                }
                Ok(res) => {
                    eprintln!("[Ollama] Error status: {}", res.status());
                    format!("[Error de conexión con el modelo: {}]", res.status())
                }
                Err(e) => {
                    eprintln!("[Ollama] Connection error: {}", e);
                    "El Dungeon Master necesita un momento para recomponerse... (modelo no disponible)".to_string()
                }
            }
        }
    }

    pub async fn generate_embeddings(&self, text: &str) -> Vec<f64> {
        if self.provider == "odysseus" || self.provider == "openai_compatible" {
            let url = format!("{}/embeddings", self.host.trim_end_matches('/'));
            let mut req = self.client.post(&url).header("Content-Type", "application/json");
            if let Some(ref key) = self.api_key {
                req = req.header("Authorization", format!("Bearer {}", key));
            }

            let payload = serde_json::json!({
                "model": self.default_model,
                "input": text
            });

            match req.json(&payload).send().await {
                Ok(res) if res.status().is_success() => {
                    if let Ok(data) = res.json::<Value>().await {
                        if let Some(arr) = data["data"][0]["embedding"].as_array() {
                            return arr.iter().filter_map(|v| v.as_f64()).collect();
                        }
                    }
                }
                _ => {}
            }
        } else {
            let url = format!("{}/api/embeddings", self.host);
            let payload = serde_json::json!({
                "model": self.default_model,
                "prompt": text,
                "keep_alive": "10m"
            });

            match self.client.post(&url).json(&payload).send().await {
                Ok(res) if res.status().is_success() => {
                    if let Ok(data) = res.json::<Value>().await {
                        if let Some(arr) = data["embedding"].as_array() {
                            return arr.iter().filter_map(|v| v.as_f64()).collect();
                        }
                    }
                }
                _ => {}
            }
        }
        Vec::new()
    }

    pub async fn classify_intent(&self, user_text: &str, model: Option<&str>) -> String {
        let system_prompt = "Eres un clasificador de intenciones experto de D&D 5e. \
Clasifica el mensaje del jugador en una sola palabra clave de entre las siguientes:\n\
- combat_action: Si ataca, se defiende o inicia pelea.\n\
- social_action: Si habla con PNJs, intimida, persuade o engaña.\n\
- exploration_action: Si investiga una habitación, abre puertas, busca trampas.\n\
- inventory_action: Si equipa objetos, consume pociones o revisa inventario.\n\
- meta_question: Si pregunta sobre reglas, historia u opciones de juego.\n\
Responde ÚNICAMENTE con la palabra clave elegida, nada más.";

        let messages = serde_json::json!([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": format!("Mensaje del jugador: '{}'", user_text)}
        ]);

        let classification = self.generate_chat(messages.as_array().unwrap(), model).await;
        let classification_clean = classification.to_lowercase();

        let valid_intents = ["combat_action", "social_action", "exploration_action", "inventory_action", "meta_question"];
        for vi in &valid_intents {
            if classification_clean.contains(vi) {
                return vi.to_string();
            }
        }

        // Heuristic fallback
        let user_lower = user_text.to_lowercase();
        if ["ataco", "golpeo", "lanzo", "espada", "arco", "iniciativa"].iter().any(|&w| user_lower.contains(w)) {
            "combat_action".to_string()
        } else if ["hablo", "pregunto", "digo", "grito"].iter().any(|&w| user_lower.contains(w)) {
            "social_action".to_string()
        } else if ["miro", "busco", "investigo", "abro", "puerta"].iter().any(|&w| user_lower.contains(w)) {
            "exploration_action".to_string()
        } else if ["equipo", "tomo", "pocion", "oro", "inventario"].iter().any(|&w| user_lower.contains(w)) {
            "inventory_action".to_string()
        } else {
            "meta_question".to_string()
        }
    }
}
