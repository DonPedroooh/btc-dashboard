import yagmail

def send_email_with_chart(subject, message, chart_path):
    # Dein Gmail-Konto
    sender = "peter.stengele@gmail.com"

    # Dein App-Passwort (kein normales Gmail-Passwort!)
    app_password = 'vmpnnopfaccwvfwc'  # ← Ersetze das hier

    # Empfängeradresse
    receiver = "peter.stengele@gmail.com"

    # E-Mail versenden
    yag = yagmail.SMTP(user=sender, password=app_password)
    yag.send(to=receiver, subject=subject, contents=message, attachments=chart_path)
    print("✅ E-Mail erfolgreich gesendet.")

