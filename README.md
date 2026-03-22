# 🛠️ CLI-Functions: O Hub de Superpoderes para seu Agente de Terminal

### 🚀 Do que se trata?
O **CLI-Functions** é um ecossistema modular desenhado para expandir drasticamente a capacidade operacional de agentes de terminal como **Codex**, **Claude Code**, **Gemini CLI** e outros. 

Este repositório não é apenas uma coleção de código; é um **hub de capacidades em expansão** que combina scripts de execução bruta com "Skills" (conhecimento procedimental). O objetivo é transformar conversas em ações reais, seguras e eficientes diretamente no seu sistema.

---

### 💡 A Estratégia: Scripts + Skills
Nossa estratégia baseia-se em dois pilares fundamentais que superam modelos de assistência passiva:

1.  **Terminal Scripts:** Ferramentas genéricas e potentes que dão ao agente acesso a APIs e funções do sistema que ele não teria nativamente.
2.  **Skills (Expertise):** Arquivos que codificam o "como fazer". Enquanto ferramentas comuns dizem ao agente *o que* está disponível, as Skills ensinam o **workflow otimizado**, as melhores práticas e como encadear ferramentas para resolver problemas complexos sem se perder.

**Benefícios vs. Agentes 24/7:**
- **Agnóstico:** Funciona em qualquer agente de terminal, sem depender de uma infraestrutura proprietária ou serviços de background pesados.
- **Portabilidade:** Cada script é salvo de forma genérica para ser adaptado a qualquer ambiente.
- **Contexto Otimizado:** Ao carregar uma Skill, o agente recebe apenas as instruções necessárias para a tarefa, economizando tokens e reduzindo alucinações.

---

### 🧩 Organização do Repositório
O hub é organizado de forma que cada projeto seja independente e autoexplicativo:

- **Pastas de Projetos:** Cada ferramenta (Steam, Google, YouTube, etc.) possui seu próprio diretório com um `README.md` específico e requisitos próprios.
- **MCP Skills (Model Context Protocol):** 
  > **A Ponte que Faltava:** Notamos que a maioria dos MCPs (como o do GitHub) entrega ferramentas "cruas" para a IA. Sem instruções claras, o agente muitas vezes falha em workflows complexos. 
  > 
  > No **CLI-Functions**, desenvolvemos Skills dedicadas para MCPs, fornecendo ao agente os manuais de instruções e os fluxos de trabalho que não vêm por padrão nessas integrações.

---

### ⚙️ Configuração e Personalização
Como "cada computador é um computador", os caminhos (paths) e dependências variam. 

**Recomendação:** Use o próprio assistente de terminal que você está utilizando para configurar as ferramentas deste repositório. Peça a ele para:
- Analisar o `SKILL.md` ou o `README.md` do projeto desejado.
- Setar os paths adequados para o seu sistema operacional.
- Configurar arquivos específicos de integração (como o `agents\openai.yaml` exigido por agentes como o Codex).

---

### 📁 Capacidades Atuais
Atualmente, o hub conta com integrações para:
- **GitHub MCP Skills:** Elevando o uso do MCP oficial com workflows avançados.
- **Google CLI:** Gestão de Gmail, Drive e Calendar.
- **Steam CLI:** Resolução de metadados e controle de biblioteca.
- **YouTube CLI:** Extração de metadados, buscas e transcrições.

---

### 📈 Expansão Contínua
Este repositório é um organismo vivo. Novas capacidades, scripts e skills são adicionados conforme novas necessidades de automação e integração surgem no dia a dia do desenvolvimento assistido por IA.

---
> *"Dando braços e cérebro para a sua IA de terminal."*
