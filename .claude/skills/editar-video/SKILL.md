---
name: editar-video
description: Edita um vídeo bruto (talking head, aula, short, reel, showreel) com cortes, motion graphics, B-roll, legendas e sound design usando transcrição + HyperFrames + ffmpeg, com loop de verificação visual. Use sempre que o usuário colocar/apontar um arquivo de vídeo e pedir para editar, cortar, animar, transformar em short/reel/aula ou "deixar engajante".
---

# Editar vídeo com IA (transcrever → cortar → planejar beats → animar → verificar)

Pipeline baseado no vídeo "Opus 5.5 Just Changed Video Editing Forever" (Nate Herk, 2026). A ideia central: o usuário descreve em linguagem natural o que quer (inclusive a *emoção* / vibe), e o agente faz todo o resto — transcrição, cortes, motion design, B-roll, som — e só entrega depois de assistir e corrigir o próprio resultado.

## Ferramentas

| Função | Ferramenta | Observação |
|---|---|---|
| Cortes, concatenação, áudio, frames para inspeção | `ffmpeg` / `ffprobe` (já instalado em `/opt/homebrew/bin`) | |
| Motion graphics / composição | **HyperFrames** (`npx hyperframes`, repo `github.com/heygen-com/hyperframes`) | Escreve cenas em HTML/CSS/JS e renderiza em vídeo. Gratuito. Leia o README do repo na primeira vez para confirmar os comandos atuais (`init`, `preview`, `render`). |
| Transcrição com timestamps por palavra | Whisper local (`brew install whisper-cpp` ou `pip install openai-whisper` em venv) — grátis, mais lento; **ou** ElevenLabs Speech-to-Text API (pago por uso, mais rápido; precisa `ELEVENLABS_API_KEY`) | **Configurado**: `whisper-cli` (brew whisper-cpp) + modelo `~/.cache/whisper/ggml-large-v3-turbo.bin`. Uso: `whisper-cli -m <modelo> -f audio.wav -l pt -ojf -osrt -of <saida> -ml 1 -sow` (JSON por palavra). |
| Geração de imagens/vídeos (B-roll sintético) | API de geração que o usuário tiver (ex.: Kling para imagem→vídeo) | Só use se houver chave configurada; senão, use screenshots/assets reais. |
| B-roll real / screenshots | Browser (Claude in Chrome) para capturar sites, logos, screenshots | Prefira assets reais da marca quando o vídeo é sobre ela. |

Trabalhe em `projects/<nome-do-video>/` dentro deste repositório: `source/`, `transcript/`, `cuts/`, `composition/` (HyperFrames), `assets/`, `renders/`, `review/` (frames de verificação).

## Antes de começar: alinhar a intenção

Se o pedido não deixar claro, pergunte (numa única rodada, no máximo 3–4 perguntas):
1. **Formato**: talking head com overlays, aula/curso, short vertical (9:16), reel/showreel, sizzle de evento.
2. **Estilo**: ex. clean com liquid glass; whiteboard desenhado à mão; minimalista com bullet points; alta energia sincronizado com a batida; identidade de uma marca específica.
3. **Beats obrigatórios**: "quando eu disser X, aparece Y ali". Quanto mais específico, mais alinhado o resultado.
4. **Liberdade criativa**: pode adicionar ideias próprias (zooms sutis, cenas extras) ou só o que foi pedido?

Aceite descrições emocionais ("quero que pareça épico", "tom amigável, como explicar pra uma criança") — traduza a emoção em decisões concretas de ritmo, tipografia, cor, música e movimento.

Se o usuário fornecer um **vídeo de referência/inspiração**, analise-o primeiro (extraia frames com ffmpeg, observe ritmo, tipografia, transições, paleta, uso de som) e escreva por que ele funciona antes de editar.

## Os 5 passos

### 1. Transcrever (essencial)
- Gere transcrição com **timestamps por palavra** (JSON + SRT) em `transcript/`.
- É o que permite que animações entrem no momento exato em que a palavra é dita e que o agente entenda a história para decidir o que cortar e destacar.
- Extraia o áudio antes: `ffmpeg -i source/in.mp4 -vn -ac 1 -ar 16000 transcript/audio.wav`.

### 2. Cortar
- Remova **erros, repetições, falsos começos** e **tempo morto** (silêncios longos, pausas, trechos sem conteúdo) usando a transcrição + detecção de silêncio (`ffmpeg -af silencedetect=noise=-35dB:d=0.6`).
- Mantenha respiros naturais (~0,1–0,2 s de margem em cada corte) para não soar picotado; evite cortes no meio de palavras.
- Gere uma lista de cortes (EDL) em `cuts/cuts.json`, renderize `cuts/clean.mp4` e **retranscreva** (ou recalcule os timestamps) para o vídeo limpo.
- Às vezes o usuário quer só esta etapa ("só limpa os erros") — nesse caso pare aqui e entregue.

### 3. Planejar os beats
- Escreva `composition/beats.md`: uma tabela `tempo | fala | o que entra na tela | posição | animação | som`.
- Inclua primeiro os beats pedidos pelo usuário, depois (se permitido) os seus próprios.
- Mostre o plano ao usuário antes de renderizar quando o vídeo for longo ou os pedidos forem ambíguos; para pedidos "one-shot" claros, siga direto.

### 4. Construir (HyperFrames + assets)
Aplique estas regras de gosto, que foram o que fez os exemplos funcionarem:
- **Legibilidade sempre**: todo texto/logo sobre o vídeo precisa de um card de fundo (liquid glass/blur translúcido) ou overlay/gradiente escuro. Nada flutuando ilegível sobre a imagem.
- **Posicionamento intencional**: se a pessoa aponta para um lado, o elemento aparece desse lado. Use os lados esquerdo/direito do quadro para B-roll e cards, sem cobrir o rosto.
- **Palavras-chave destacadas**: frases de impacto aparecem em lower third com a palavra-chave em destaque (cor/peso), sincronizadas palavra a palavra.
- **Mostrar, não só dizer**: quando o falante menciona algo (um site, uma ferramenta, um resultado), traga a prova — screenshot, gravação de tela, logo real, imagem gerada.
- **Movimento sutil constante**: zoom-in lento no talking head, punch-ins em frases fortes; nada de tela estática por muito tempo.
- **Variação de layout** (aulas/tutoriais): alternar tela cheia da câmera, câmera em crop arredondado sobre fundo minimalista, split-screen (metade gráfico, metade rosto) e takeover total do gráfico.
- **Aula/curso**: bullets grandes, poucas palavras, só os takeaways; imagens simples de apoio.
- **Short/reel**: ritmo rápido, cortes frequentes, B-roll de fundo trocando, música com cortes na batida, SFX em cada entrada de elemento.
- **Marca**: se o vídeo é sobre uma marca/produto, pesquise e use tipografia, cores, linguagem visual e assets reais dela — a identidade deve ser inconfundível.
- **Sound design**: whooshes/pops nas entradas, trilha com volume abaixo da voz (ducking ~-18 a -22 dB sob fala), sincronizar transições com as batidas.
- Imagens geradas podem virar vídeo (imagem→vídeo) para dar vida a cenas; mantenha consistência de estilo entre elas.

### 5. Loop de verificação (o mais importante)
Nunca entregue a primeira versão sem assisti-la:
1. Renderize em `renders/vN.mp4`.
2. Extraia frames nos momentos de cada beat e em intervalos regulares (`ffmpeg -ss T -i renders/vN.mp4 -frames:v 1 review/vN_T.png`) e **olhe as imagens** (Read).
3. Verifique: texto legível e sem cortar nas bordas, elementos não cobrindo o rosto, sincronia com a fala (compare timestamps com a transcrição), cortes sem palavras decepadas, áudio sem picos/clipping (`ffmpeg -af ebur128` ou `volumedetect`), duração e proporção corretas.
4. Corrija e renderize a próxima versão. Repita até que você mesmo aprovaria o vídeo.
5. Entregue com um resumo curto: o que foi feito, beats criativos que você adicionou por conta própria e limitações conhecidas.

## Notas técnicas aprendidas (HyperFrames)
- `npx hyperframes init composition --non-interactive --skip-transcribe --video cuts/clean.mp4 --resolution landscape`; render: `npx hyperframes render -o ../renders/vN.mp4` (~1x tempo real).
- **Emojis não renderizam** no Chrome headless: use SVG inline para ícones.
- Não deixe outro `.html` com `data-composition-id` dentro de `composition/` (lint acusa root duplicado) — templates ficam fora.
- Não use `transform` no CSS de elementos que o GSAP anima; use `tl.fromTo` com o estado inicial.
- `backdrop-filter` (liquid glass) funciona no render.
- Áudio sai ~-20 LUFS: normalize no final com `loudnorm=I=-14:TP=-1.5`.

- **iPhone (.MOV HEVC HLG/HDR)**: converta para SDR antes de tudo, senão fica lavado no Instagram: `zscale=tin=arib-std-b67:pin=bt2020:min=bt2020nc:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0:peak=4,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=1080:1920,eq=saturation=0.88`. Use `-map 0:a:0` (há 2 faixas de áudio).
- O Whisper erra "Claude Code" → "Cloud Code": use `--prompt "Claude Code"` e um dicionário de correções.
- Confira se o começo do take não está cortado no meio de uma palavra antes de usá-lo como abertura.
- **Instagram 9:16 – zonas seguras**: cards de y≈230 a 560, legendas y≈1250–1470 (sobre o peito), CTA y≈1200–1500; nada abaixo de ~1560 nem na coluna direita inferior (UI).
- **Variações para anúncio**: modelo em `projects/img_7252/` — `cuts/spec.py` define frases (tempos do source) e a ordem de cada variação; `make_cuts.py` → `transcribe_cuts.py` (retranscreve cada corte) → `gen.py <nome>` gera a composição com overlays ancorados em palavras de cada frase. Mostre o gancho já no frame 0 (thumbnail) e congele ~1,2 s no final para o CTA.

- **Validar pontos de corte dentro de fala emendada**: teste candidatos (ex. a cada 30–40 ms) com `aselect='between(t,a,b)+between(t,c,d)'` e transcreva cada teste; escolha o primeiro corte em que o Whisper lê a frase limpa. Descarte palavras que o Whisper "ouve" no final congelado (alucinação, ex. "Legenda por…").
- Legendas: não quebre bloco depois de preposição/artigo (de, a, o, em, com…) nem entre "Claude" e "Code".

- **Tela dividida 9:16** (modelo em `projects/img_7252/split_template.html` + `gen_split.py`): metade de cima (1080×960) = cena animada por frase (fundo escuro com grid e blobs em movimento; conteúdo entre y≈150 e 870); metade de baixo = câmera recortada centrada no rosto (`top:-420px`); legenda logo abaixo da divisória (y≈1010). As cenas são encadeadas (cada uma vai até a próxima começar), então a metade de cima nunca fica vazia. Cenas curtas (~1,4 s) pedem animações rápidas: tudo precisa terminar antes da troca de cena. Títulos grandes com `max-width` para quebrar linha em vez de vazar.

## Depois da entrega: melhorar esta skill
Quando o usuário der feedback ("gostei disso", "não faça aquilo", "sempre use esta fonte"), pergunte se deve registrar aqui e adicione na seção abaixo. Se ele repetir um pedido duas vezes, é sinal de que deve virar regra permanente. Estilos recorrentes (ex. um formato de reel específico) podem virar skills próprias em `.claude/skills/`.

## Preferências do usuário
<!-- Preencha conforme o feedback: marca, fontes, cores, formato padrão, tom, o que evitar. -->
- **Mensagem acima de tudo**: depois de cortar/reordenar, leia a transcrição completa de cada vídeo final como um espectador. Qualquer trecho sem sentido (frase truncada, "seja estar…", take cortado ininteligível, repetição colada tipo "4 dias… 4 dias") deve ser removido ou recortado — mesmo que leve junto uma informação secundária. Cortar é bom, texto sem sentido não.
- Legenda tem que bater com o que foi dito: corrija só erros de reconhecimento (ex.: Cloud→Claude), nunca "melhore" palavras faladas.
- Sempre entregue as legendas (.srt + .txt) junto com cada vídeo.
