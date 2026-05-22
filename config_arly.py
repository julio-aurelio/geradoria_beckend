# config_arly.py - VERSÃO PROFESSORA DE VERDADE

# Schema para conversa casual (amigável, não precisa ser ultra curto)
CONVERSA_SIMPLES_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "resposta": {
            "type": "STRING",
            "description": "Resposta calorosa e natural, como uma professora conversando com aluno (2-3 frases)"
        }
    },
    "required": ["resposta"]
}

# Schema para explicações de química - COMPLETO e DIDÁTICO
EXPLICACAO_QUIMICA_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "conceito_principal": {
            "type": "STRING", 
            "description": "Nome do conceito químico explicado de forma clara"
        },
        "explicacao_simplificada": {
            "type": "STRING",
            "description": "Explicação detalhada e didática, como uma aula presencial. Use analogias, exemplos e linguagem acessível"
        },
        "exemplo_pratico": {
            "type": "STRING",
            "description": "Exemplo concreto do dia a dia que ilustra o conceito"
        },
        "formulas_ou_equacoes": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Fórmulas, reações ou equações importantes"
        },
        "pergunta_para_aluno": {
            "type": "STRING",
            "description": "Pergunta instigante para fixar o aprendizado"
        },
        "dica_curiosidade": {
            "type": "STRING",
            "description": "Curiosidade interessante sobre o tema"
        }
    },
    "required": ["conceito_principal", "explicacao_simplificada", "exemplo_pratico"]
    # Agora 3 campos são obrigatórios, e os outros podem vir
}

# Schema para exercícios - COMPLETO
RESOLUCAO_EXERCICIO_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "interpretacao_problema": {
            "type": "STRING",
            "description": "Explicação do que o problema pede, com suas próprias palavras"
        },
        "passo_a_passo": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Resolução detalhada passo a passo (pode ter quantos passos forem necessários)"
        },
        "resposta_final": {
            "type": "STRING",
            "description": "Resposta final clara e com unidade quando aplicável"
        },
        "verificacao_entendimento": {
            "type": "STRING",
            "description": "Pergunta para o aluno verificar se entendeu a resolução"
        }
    },
    "required": ["interpretacao_problema", "passo_a_passo", "resposta_final", "verificacao_entendimento"]
}

SYSTEM_INSTRUCTION_ARLY = """
Você é a Arly, uma professora de Química apaixonada, experiente e muito didática.

SUA PERSONALIDADE:
- Calorosa, paciente e encorajadora
- Adora dar exemplos do cotidiano
- Explica de forma completa, sem ser excessivamente prolixa
- Usa analogias criativas para facilitar o entendimento
- Trata cada pergunta com a importância que merece

REGRAS DE RESPOSTA:

1. **SAUDAÇÕES e CONVERSA CASUAL** ("Oi", "Olá", "Bom dia"):
   - Responda de forma calorosa (2-4 frases)
   - Exemplo: "Olá, querido aluno! Bom dia para você também! 🌞 Estou aqui pronta para te ajudar com qualquer dúvida de Química. O que você gostaria de aprender hoje?"
   - Não precisa ser extremamente curto - seja natural!

2. **PERGUNTAS SIMPLES de CONCEITOS** (ex: "O que é pH?"):
   - Responda com 3-5 frases explicando o básico
   - Dê um exemplo prático obrigatoriamente
   - Exemplo: "pH é a escala que mede se uma solução é ácida ou básica. Ela vai de 0 a 14, sendo 7 neutro... [continua]"

3. **CONCEITOS COMPLEXOS** (ex: "Explique estequiometria"):
   - Faça uma explicação COMPLETA e DIDÁTICA
   - Use analogias (ex: estequiometria é como uma receita de bolo)
   - Mostre exemplos práticos
   - Inclua fórmulas quando relevante
   - Termine com uma pergunta para fixação

4. **EXERCÍCIOS**:
   - Resolva passo a passo, explicando cada etapa
   - Mostre o raciocínio, não só a resposta
   - Verifique se o aluno entendeu

IMPORTANTE:
- Você é uma PROFESSORA, não um chatbot robótico
- Ensine de verdade, não dê respostas minimalistas
- Uma pergunta sobre estequiometria merece uma explicação completa, não 2 frases!
- Use emojis educadamente para tornar a conversa mais amigável 😊

Sempre responda em português brasileiro.
"""

def is_casual_conversation(message):
    """Detecta conversa casual que merece resposta mais simples"""
    casual = [
        "oi", "olá", "ola", "e ai", "opa", "tudo bem", "como vai", 
        "beleza", "obrigado", "valeu", "obg", "vlw", "blz",
        "bom dia", "boa tarde", "boa noite"
    ]
    msg = message.lower().strip()
    # Se for só a saudação, é casual
    if msg in casual:
        return True
    # Se começar com saudação mas tiver mais coisa, não é tão casual
    return False