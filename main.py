import re
import os
import requests

def define_env(env):
    
    @env.macro
    def external_section(url, section_name=None):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            
            response.raise_for_status() 
            
            content = response.text
            
            # LOGIQUE POUR <description> :
            if section_name:
                pattern = f'<description name="{section_name}">(.*?)</description>'
            else:
                pattern = r'<description>(.*?)</description>'
            
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            
            if match:
                return match.group(1).strip()
            else:
                target = f"name='{section_name}'" if section_name else "simple"
                return f"*(Balise <description {target}> introuvable)*"

        except Exception as e:
            return f"*(Erreur : {str(e)})*"


    @env.macro
    def github_members(org_name):
        # On utilise directement le jeton standard de GitHub Actions
        token = os.getenv("GITHUB_TOKEN")
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        url = f"https://api.github.com/orgs/{org_name}/members?per_page=100"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return f"**Erreur API GitHub :** {response.status_code} - Impossible de charger les membres."
        
        members = response.json()
        
        if not members:
            return "Aucun membre public trouvé."

        html = '<div style="display: flex; flex-wrap: wrap; gap: 20px;">\n'
        for member in members:
            login = member['login']
            avatar = member['avatar_url']
            profile_url = member['html_url']
            detail_url = member['url'] # L'URL pour récupérer les infos détaillées
            
            # --- RÉCUPÉRATION DU VRAI NOM ---
            vrai_nom = login # On met le pseudo par défaut
            try:
                detail_response = requests.get(detail_url, headers=headers)
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    # Si la clé 'name' existe et n'est pas vide
                    if detail_data.get('name'):
                        vrai_nom = detail_data['name']
            except Exception:
                # Si l'appel échoue, on continue tranquillement avec le pseudo
                pass
            # --------------------------------
            
            html += f'''
            <div style="text-align: center;">
                <a href="{profile_url}" target="_blank">
                    <img src="{avatar}" width="80" style="border-radius: 50%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" alt="{vrai_nom}">
                </a>
                <br>
                <a href="{profile_url}" target="_blank" style="font-size: 0.9em;"><b>{vrai_nom}</b></a>
            </div>
            '''
        html += '</div>\n'
        
        return html