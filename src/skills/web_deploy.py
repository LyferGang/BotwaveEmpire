"""
Web Deployment Skill
Deploy websites to Cloudflare Pages using secure credential management.
"""

import subprocess
import os
from typing import Dict, Any
from pathlib import Path

from core.secrets import secrets


class WebDeploySkill:
    """
    Skill for deploying websites to Cloudflare Pages.

    Uses credentials from environment only - never hardcoded.
    """

    def __init__(self):
        self.required_secrets = ['cloudflare_token', 'cloudflare_account', 'cloudflare_zone']

    def deploy(self, source_dir: str, project_name: str = "botwave") -> Dict[str, Any]:
        """
        Deploy website to Cloudflare Pages.

        Args:
            source_dir: Path to website source files
            project_name: Cloudflare Pages project name

        Returns:
            Deployment result
        """
        # Validate credentials exist
        if not all(secrets.has(key) for key in self.required_secrets):
            missing = [k for k in self.required_secrets if not secrets.has(k)]
            return {
                "status": "error",
                "message": f"Missing Cloudflare credentials: {missing}",
                "hint": "Set CF_API_TOKEN, CF_ACCOUNT_ID, and CF_ZONE_ID in .env"
            }

        cf_token = secrets.get('cloudflare_token')
        cf_account = secrets.get('cloudflare_account')
        cf_zone = secrets.get('cloudflare_zone')

        try:
            # Check if wrangler is available
            result = subprocess.run(
                ['which', 'wrangler'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": "Wrangler CLI not found. Install with: npm install -g wrangler",
                    "install_cmd": "npm install -g wrangler"
                }

            # Deploy using wrangler
            deploy_cmd = [
                'wrangler', 'pages', 'deploy', source_dir,
                '--project-name', project_name,
                '--branch', 'main'
            ]

            env = os.environ.copy()
            env['CLOUDFLARE_API_TOKEN'] = cf_token
            env['CLOUDFLARE_ACCOUNT_ID'] = cf_account

            result = subprocess.run(
                deploy_cmd,
                capture_output=True,
                text=True,
                env=env,
                cwd=source_dir
            )

            if result.returncode == 0:
                # Purge cache
                self._purge_cache(cf_token, cf_zone)

                return {
                    "status": "success",
                    "message": f"Deployed {project_name} to Cloudflare Pages",
                    "output": result.stdout
                }
            else:
                return {
                    "status": "error",
                    "message": "Deployment failed",
                    "error": result.stderr
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Deployment error: {str(e)}"
            }

    def _purge_cache(self, token: str, zone_id: str) -> None:
        """Purge Cloudflare cache after deployment."""
        import requests

        try:
            response = requests.post(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json={"purge_everything": True}
            )

            if response.status_code == 200:
                print("[WebDeploy] Cache purged successfully")
            else:
                print(f"[WebDeploy] Cache purge failed: {response.status_code}")

        except Exception as e:
            print(f"[WebDeploy] Cache purge error: {e}")

    def build_website(self, template_dir: str, output_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build website from templates with dynamic content.

        Args:
            template_dir: Source templates directory
            output_dir: Output directory for built site
            context: Template variables

        Returns:
            Build result
        """
        try:
            import shutil
            from pathlib import Path

            # Copy template files
            template_path = Path(template_dir)
            output_path = Path(output_dir)

            if output_path.exists():
                shutil.rmtree(output_path)

            shutil.copytree(template_path, output_path)

            # Process templates (simple variable substitution)
            for html_file in output_path.glob("**/*.html"):
                content = html_file.read_text()

                # Replace template variables
                for key, value in context.items():
                    placeholder = f"{{{{ {key} }}}}"
                    content = content.replace(placeholder, str(value))

                html_file.write_text(content)

            return {
                "status": "success",
                "message": f"Website built to {output_dir}",
                "files_processed": len(list(output_path.glob("**/*")))
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Build failed: {str(e)}"
            }
