import urllib.request
import re

def define_env(env):
    @env.macro
    def external_section(url, section_name=None):
        try:
            # On se fait passer pour un navigateur
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
                
                # LOGIQUE POUR <description> :
                if section_name:
                    # Cas 1 : Tu as précisé un nom (ex: "resume") dans index.md
                    # On cherche <description name="resume"> ... </description>
                    pattern = f'<description name="{section_name}">(.*?)</description>'
                else:
                    # Cas 2 : Tu n'as rien précisé
                    # On cherche juste <description> ... </description>
                    pattern = r'<description>(.*?)</description>'
                
                # Recherche (re.DOTALL permet de prendre tout le texte, même sur plusieurs lignes)
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                
                if match:
                    return match.group(1).strip()
                else:
                    target = f"name='{section_name}'" if section_name else "simple"
                    return f"*(Balise <description {target}> introuvable)*"

        except Exception as e:
            return f"*(Erreur : {str(e)})*"