import streamlit as st
import pandas as pd
from io import StringIO
import csv
import io

# Add HF / env imports
import os
import requests
from dotenv import load_dotenv
load_dotenv()

# Initialize local DB and session storage for created job ids
import db
# create tables if not present
try:
    db.create_tables()
except Exception:
    # don't crash the app if DB creation fails, show later when used
    pass

if 'last_created_job_ids' not in st.session_state:
    st.session_state['last_created_job_ids'] = []

# Title of the app
st.title('Job Application Requirements Analyzer')

# Instruction text
st.write("""
Upload a CSV file containing job applications, and this app
will extract and analyze the requirements from each application.
""")

# File uploader to accept CSV files
uploaded_file = st.file_uploader("Choose a file")

# Optional: allow manually pasting CSV/TSV content (or just the Requirements column)
manual_text = st.text_area(
    "Or paste CSV/TSV text here (you can paste the whole file or just the Requirements column):",
    height=200,
)

# Button to process pasted text (user requested an explicit action)
process_manual = st.button("Process pasted text")

# Simple requirement parser function usable for both pasted text and uploaded files
def parse_requirements(cell):
    import re
    if pd.isna(cell):
        return []
    text = str(cell)
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Prefer splitting on blank lines (paragraphs)
    if '\n\n' in text:
        parts = [p.strip() for p in text.split('\n\n') if p.strip()]
    elif '\n' in text:
        # Split on single newlines
        parts = [p.strip() for p in text.split('\n') if p.strip()]
    else:
        # Split into sentences using punctuation as fallback
        sentence_end = re.compile(r'(?<=[.!?])\s+')
        parts = [p.strip() for p in sentence_end.split(text) if p.strip()]

    # If we still have a single long part that looks like a comma-separated list,
    # and no sentence punctuation, split on commas as a last resort.
    if len(parts) == 1 and parts[0].count(',') >= 2 and parts[0].count('.') == 0:
        parts = [p.strip() for p in parts[0].split(',') if p.strip()]

    return parts

# If the user clicked the button, parse the pasted text
if process_manual:
    if manual_text and manual_text.strip():
        try:
            decoded = manual_text
            used_encoding = 'manual'
            sample = decoded[:10000]
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
                delimiter = dialect.delimiter
            except Exception:
                delimiter = None

            sio = io.StringIO(decoded)
            if delimiter:
                df = pd.read_csv(
                    sio,
                    sep=delimiter,
                    engine='python',
                    quoting=csv.QUOTE_MINIMAL,
                    escapechar='\\',
                    on_bad_lines='skip'
                )
            else:
                df = pd.read_csv(
                    sio,
                    sep=None,
                    engine='python',
                    quoting=csv.QUOTE_MINIMAL,
                    escapechar='\\',
                    on_bad_lines='skip'
                )
        except Exception as e:
            st.error(f"Error parsing pasted text: {e}")
            df = pd.DataFrame()

        # If parsing produced a dataframe, show same analysis as for uploaded files
        if 'df' in locals() and not df.empty:
            st.write("## Parsed Job Applications (from pasted text)")
            st.write(df)

            if 'Requirements' in df.columns:
                requirements = df['Requirements'].apply(parse_requirements)

                # Persist parsed rows into DB and keep created job ids in session state
                try:
                    created_ids = []
                    for i, req_list in enumerate(requirements):
                        raw = df['Requirements'].iloc[i]
                        try:
                            job_id = db.insert_job(source='pasted', row_index=i, raw_requirements=str(raw))
                        except Exception as e:
                            st.warning(f"DB insert_job failed: {e}")
                            job_id = None
                        if job_id:
                            for p in req_list:
                                try:
                                    db.insert_requirement(job_id, p)
                                except Exception:
                                    pass
                            created_ids.append(job_id)
                    st.session_state['last_created_job_ids'] = created_ids
                except Exception:
                    # non-fatal
                    pass

                st.write("## Analyzed Requirements")
                all_requirements = []
                for idx, req_list in enumerate(requirements):
                    st.write(f"Application {idx+1} Requirements:", req_list)
                    all_requirements.extend(req_list)

                # Adding a text area for copying/pasting requirements
                st.write("### Copy the Requirements Below:")
                requirements_text = "\n".join(all_requirements)
                st.text_area("Requirements", value=requirements_text, height=300)
            else:
                st.write("No 'Requirements' column found in the pasted data.")
    else:
        st.warning("Paste some text into the box before pressing the button.")

# If a file is uploaded
if uploaded_file is not None:
    try:
        # Read raw bytes from the uploaded file
        content_bytes = uploaded_file.read()

        # Empty file check
        if not content_bytes or not content_bytes.strip():
            st.error("The uploaded file is empty. Please upload a valid CSV/TSV file.")
            df = pd.DataFrame()
        else:
            # Try common encodings
            decoded = None
            for enc in ("utf-8", "ISO-8859-1", "cp1252"):
                try:
                    decoded = content_bytes.decode(enc)
                    used_encoding = enc
                    break
                except Exception:
                    decoded = None
            if decoded is None:
                # Fallback with replacement to avoid crashes
                decoded = content_bytes.decode("utf-8", errors="replace")
                used_encoding = "utf-8-replace"

            # Detect delimiter using a sample
            sample = decoded[:10000]
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
                delimiter = dialect.delimiter
            except Exception:
                delimiter = None

            sio = io.StringIO(decoded)

            # DEBUG: show detected encoding, delimiter and a sample to help troubleshooting
            try:
                st.write("DEBUG: detected encoding:", used_encoding)
            except NameError:
                st.write("DEBUG: detected encoding: <not set>")
            st.write("DEBUG: detected delimiter:", repr(delimiter))
            st.text_area("DEBUG: file sample (first 1000 chars)", value=sample[:1000], height=200)

            # Read with detected delimiter or let pandas infer
            if delimiter:
                df = pd.read_csv(
                    sio,
                    sep=delimiter,
                    engine='python',
                    quoting=csv.QUOTE_MINIMAL,
                    escapechar='\\',
                    on_bad_lines='skip'
                )
            else:
                df = pd.read_csv(
                    sio,
                    sep=None,
                    engine='python',
                    quoting=csv.QUOTE_MINIMAL,
                    escapechar='\\',
                    on_bad_lines='skip'
                )
    except pd.errors.EmptyDataError:
        st.error("The uploaded file appears to be empty or doesn't contain valid CSV data. Please check the file format.")
        df = pd.DataFrame()
    except Exception as e:
        st.error(f"Error reading the file: {e}")
        df = pd.DataFrame()

    # Display the dataframe
    if not df.empty:
        st.write("## Uploaded Job Applications")
        st.write(df)

        # Extract requirements column (assumed to be named 'Requirements')
        if 'Requirements' in df.columns:
            requirements = df['Requirements'].apply(parse_requirements)

            # Persist uploaded rows into DB and keep created job ids in session state
            try:
                created_ids = []
                source_name = getattr(uploaded_file, 'name', 'uploaded') if uploaded_file is not None else 'uploaded'
                for i, req_list in enumerate(requirements):
                    raw = df['Requirements'].iloc[i]
                    try:
                        job_id = db.insert_job(source=source_name, row_index=i, raw_requirements=str(raw))
                    except Exception as e:
                        st.warning(f"DB insert_job failed: {e}")
                        job_id = None
                    if job_id:
                        for p in req_list:
                            try:
                                db.insert_requirement(job_id, p)
                            except Exception:
                                pass
                        created_ids.append(job_id)
                st.session_state['last_created_job_ids'] = created_ids
            except Exception:
                pass

            st.write("## Analyzed Requirements")
            all_requirements = []
            for idx, req_list in enumerate(requirements):
                st.write(f"Application {idx+1} Requirements:", req_list)
                all_requirements.extend(req_list)
            
            # Adding a text area for copying/pasting requirements
            st.write("### Copy the Requirements Below:")
            requirements_text = "\n".join(all_requirements)
            st.text_area("Requirements", value=requirements_text, height=300)

            # Hugging Face integration
            HF_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN")
            HF_MODEL = "google/flan-t5-large"
            HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

            def ask_hf(prompt, max_new_tokens=400, timeout=60):
                if not HF_TOKEN:
                    raise RuntimeError("HUGGINGFACE_API_TOKEN not set in environment. Create a token at https://huggingface.co and set it in your environment or .env file.")
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_new_tokens}}
                resp = requests.post(HF_API_URL, headers=headers, json=payload, timeout=timeout)
                resp.raise_for_status()
                out = resp.json()
                if isinstance(out, list) and out and "generated_text" in out[0]:
                    return out[0]["generated_text"]
                if isinstance(out, dict) and "generated_text" in out:
                    return out["generated_text"]
                return str(out)

            if requirements_text.strip():
                if st.button("Ask HF (career coach)"):
                    prompt = f"As my career coach deliver all skills, methods, tech or knowledge that would be optimal to fulfill the following requirement of a technical position:\n\n{requirements_text}"
                    try:
                        with st.spinner("Calling Hugging Face..."):
                            answer = ask_hf(prompt, max_new_tokens=600)
                        st.subheader("HF response")
                        st.text_area("Career-coach output", value=answer, height=400)

                        # Persist the analysis into DB for the recently created jobs (if any)
                        try:
                            created = st.session_state.get('last_created_job_ids', [])
                            if created:
                                for jid in created:
                                    try:
                                        db.insert_analysis(jid, HF_MODEL, prompt, answer)
                                    except Exception:
                                        pass
                            else:
                                # fallback: insert analysis without job linkage
                                try:
                                    db.insert_analysis(None, HF_MODEL, prompt, answer)
                                except Exception:
                                    pass
                        except Exception:
                            pass
                    except Exception as e:
                        st.error(f"HF API error: {e}")
        else:
            st.write("No 'Requirements' column found in the uploaded file.")
    else:
        st.write("Please upload a valid CSV file to analyze.")
else:
    st.write("Please upload a CSV file to analyze.")