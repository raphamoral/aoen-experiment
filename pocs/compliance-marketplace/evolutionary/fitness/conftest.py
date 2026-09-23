"""
Configuração compartilhada das fitness functions.
Adiciona src/ ao PYTHONPATH para que os testes arquiteturais
possam importar os módulos do projeto.
"""

import sys
from pathlib import Path

# Garante que o raiz do projeto está no path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))