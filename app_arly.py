# app_arly.py

import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Importando o que criamos para a Arly
from config_arly import EXPLICACAO_QUIMICA_SCHEMA, SYSTEM_INSTRUCTION_ARLY, RESOLUCAO_EXERCICIO_SCHEMA

# Carrega as variáveis de ambiente e inicia o Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Verificação crítica da API key
if not GEMINI_API_KEY:
    print("❌ ERRO: GEMINI_API_KEY não encontrada no arquivo .env")
    print("📝 Crie um arquivo .env com: GEMINI_API_KEY=sua_chave_aqui")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

# Inicializa o Flask
app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# ========== FUNÇÕES DA ARLY ==========

def explicar_conceito(duvida_aluno, nivel="medio"):
    """
    Gera uma explicação química baseada na dúvida do aluno.
    
    Parâmetros:
    - duvida_aluno: string com a pergunta ou conceito a ser explicado
    - nivel: "basico", "medio" ou "avancado"
    """
    conteudo_prompt = f"""
    Aluno pergunta: {duvida_aluno}
    Nível de ensino solicitado: {nivel}
    
    Como Professora Arly, explique este conceito químico de forma clara e didática.
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",  # Modelo estável para JSON estruturado
        contents=conteudo_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION_ARLY,
            response_mime_type="application/json",
            response_schema=EXPLICACAO_QUIMICA_SCHEMA,
        )
    )
    return response.text

def resolver_exercicio(enunciado):
    """Função extra para resolução passo a passo de exercícios"""
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=f"Resolva este exercício de química: {enunciado}",
        config=types.GenerateContentConfig(
            system_instruction="Você é a Arly, professora de Química. Resolva o exercício passo a passo.",
            response_mime_type="application/json",
            response_schema=RESOLUCAO_EXERCICIO_SCHEMA,
        )
    )
    return response.text

# ========== ENDPOINTS DA API ==========

@app.route("/")
def root():
    return jsonify({
        "status": "success",
        "professora": "Arly - Professora de Química IA",
        "message": "API funcionando! Use /explicar para tirar dúvidas ou /exercicio para resolver problemas.",
        "versao": "1.0",
        "endpoints": {
            "/explicar": "POST - Envie {'pergunta': 'sua duvida', 'nivel': 'basico/medio/avancado'}",
            "/exercicio": "POST - Envie {'enunciado': 'texto do exercicio'}",
            "/quimica/aleatoria": "GET - Gera um conceito químico aleatório para estudar"
        }
    }), 200

@app.route("/explicar", methods=["POST"])
def explicar():
    """Endpoint principal para tirar dúvidas de química"""
    data = request.get_json()
    
    # Validação 1: O JSON foi enviado?
    if not data or "pergunta" not in data:
        return jsonify({
            "status": "error",
            "message": "Por favor, envie sua pergunta no formato: {'pergunta': 'O que é pH?'}"
        }), 400
    
    pergunta = data.get("pergunta", "").strip()
    nivel = data.get("nivel", "medio")  # padrão: ensino médio
    
    # Validação 2: A pergunta não está vazia
    if not pergunta:
        return jsonify({
            "status": "error",
            "message": "A pergunta não pode estar vazia."
        }), 400
    
    # Validação 3: Nível válido
    if nivel not in ["basico", "medio", "avancado"]:
        return jsonify({
            "status": "error",
            "message": "Nível inválido. Use: 'basico', 'medio' ou 'avancado'"
        }), 400
    
    try:
        # Gera a explicação da Arly
        explicacao_json_string = explicar_conceito(pergunta, nivel)
        explicacao_estruturada = json.loads(explicacao_json_string)
        
        return jsonify({
            "status": "success",
            "professora": "Arly",
            "pergunta_do_aluno": pergunta,
            "nivel": nivel,
            "aula": explicacao_estruturada
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro ao gerar explicação: {str(e)}",
            "dica": "Tente reformular sua pergunta de forma mais clara."
        }), 500

@app.route("/exercicio", methods=["POST"])
def exercicio():
    """Endpoint para resolver exercícios de química"""
    data = request.get_json()
    
    if not data or "enunciado" not in data:
        return jsonify({
            "status": "error",
            "message": "Envie o enunciado no formato: {'enunciado': 'Calcule a massa molar do H2O...'}"
        }), 400
    
    enunciado = data.get("enunciado", "").strip()
    
    if not enunciado:
        return jsonify({
            "status": "error",
            "message": "O enunciado não pode estar vazio."
        }), 400
    
    try:
        resolucao_json_string = resolver_exercicio(enunciado)
        resolucao_estruturada = json.loads(resolucao_json_string)
        
        return jsonify({
            "status": "success",
            "professora": "Arly",
            "exercicio": enunciado,
            "resolucao": resolucao_estruturada
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro ao resolver exercício: {str(e)}"
        }), 500

@app.route("/quimica/aleatoria", methods=["GET"])
def conceito_aleatorio():
    """Gera um conceito químico aleatório para estudo"""
    conceitos = [
        "O que é uma ligação iônica?",
        "Explique a tabela periódica",
        "Como funciona o pH?",
        "O que são ácidos e bases?",
        "Explique a lei de Lavoisier",
        "O que é catálise?",
        "Diferença entre solução saturada e insaturada",
        "O que é número de oxidação?",
        "Explique a radioatividade",
        "Como funciona a eletrólise?"
    ]
    
    import random
    pergunta_aleatoria = random.choice(conceitos)
    
    try:
        explicacao_json_string = explicar_conceito(pergunta_aleatoria, "medio")
        explicacao_estruturada = json.loads(explicacao_json_string)
        
        return jsonify({
            "status": "success",
            "professora": "Arly",
            "conceito_do_dia": pergunta_aleatoria,
            "aula": explicacao_estruturada
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro: {str(e)}"
        }), 500

# ========== EXECUÇÃO DO SERVIDOR ==========
if __name__ == "__main__":    
    app.run(debug=True)