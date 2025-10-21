from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_cors import CORS
import re

app = Flask(__name__)

# ✅ Aktifkan CORS untuk semua rute
CORS(app, resources={r"/*": {"origins": "*"}})

# -------------------------
# Format jawaban jadi HTML
# -------------------------
# -------------------------
# Format jawaban jadi HTML (Revisi: Menambahkan Penanganan Heading Level 3)
# -------------------------
def format_answer(answer):
    # 1. Penanganan Code Block (Multi-baris)
    def replace_code_block(match):
        content = match.group(1).strip()
        content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f"<pre><code>{content}</code></pre>"

    answer = re.sub(r"```(?:\w+)?\n([\s\S]*?)\n```", replace_code_block, answer, flags=re.MULTILINE)
    
    # 2. Penanganan Inline Code (`...`)
    answer = re.sub(r"`(.*?)`", r"<code>\1</code>", answer)
    
    # 3. Penanganan Bold (**)
    answer = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", answer)

    # 4. Penanganan Italic (* atau _)
    answer = re.sub(r"([*_])(.*?)\1", r"<em>\2</em>", answer)

    lines = answer.split("\n")
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        # 5. Penanganan Horizontal Rule (--- atau ***)
        if re.match(r"^(\*|_|-){3,}\s*$", stripped):
            new_lines.append("<hr>")
            continue

        # 6. Penanganan Heading (DIPERBARUI)
        if stripped.startswith("### "):
            new_lines.append(f"<h3>{stripped[4:].strip()}</h3>") # <--- BARIS INI DITAMBAHKAN
            continue
        if stripped.startswith("## "):
            new_lines.append(f"<h2>{stripped[3:].strip()}</h2>")
            continue
        if stripped.startswith("# "):
            new_lines.append(f"<h1>{stripped[2:].strip()}</h1>")
            continue

        # 7. Penghapusan List Logic
        # Hapus penomoran atau bullet di awal baris
        stripped = re.sub(r"^\d+\.\s*", "", stripped) 
        stripped = re.sub(r"^(\*|\-|\+)\s*", "", stripped)

        # 8. Paragraph
        # Judul (diakhiri dengan ":")
        if stripped.endswith(":"):
            if not new_lines or (not new_lines[-1].startswith("<pre>") and not new_lines[-1].endswith("</code></pre>")):
                 new_lines.append(f"<p><strong>{stripped[:-1]}:</strong></p>")
            else:
                 new_lines.append(f"<p>{stripped}</p>")
        else:
            if not new_lines or (not new_lines[-1].startswith("<pre>") and not new_lines[-1].endswith("</code></pre>")):
                 new_lines.append(f"<p>{stripped}</p>")
            else:
                 new_lines.append(stripped) 

    final_output = "\n".join(new_lines)
    
    return final_output

# -------------------------
# Endpoint halaman utama
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# Endpoint Chat
# -------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt", "")
    berat = data.get("berat")
    tinggi = data.get("tinggi")

    # Filter topik
  
    # Hitung IMT jika ada data
    imt_msg = ""
    if berat and tinggi:
        imt = berat / ((tinggi/100)**2)
        if imt < 18.5:
            kategori = "Kurus"
        elif imt < 25:
            kategori = "Normal"
        elif imt < 30:
            kategori = "Overweight"
        else:
            kategori = "Obesitas"
        imt_msg = f"IMT Anda: {imt:.1f} ({kategori})"

    # Gabungkan prompt
    full_prompt = f"{prompt}\n{imt_msg}\nBuat jawaban singkat, jelas, rapi, dengan bullet point jika perlu."

    # Inisialisasi OpenRouter (DeepSeek R1)
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    completion = client.chat.completions.create(
        model="tngtech/deepseek-r1t2-chimera:free",
        messages=[
            {
                "role": "system",
                "content": (
                    "Anda adalah Asisten Kesehatan. "
                    "Fokus menjawab hanya tentang kesehatan anak, ibu, gizi, stunting, IMT, penyakit, dan kebutuhan kalori. "
                    "Jika pengguna bertanya di luar topik tersebut, jangan jawab, cukup katakan: "
                    "'Maaf, saya hanya bisa membantu seputar kesehatan, gizi, stunting, IMT, dan kebutuhan kalori.'"
                )
            },
            {"role": "user", "content": full_prompt}
        ]
    )

    answer = completion.choices[0].message.content
    answer = format_answer(answer)

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
