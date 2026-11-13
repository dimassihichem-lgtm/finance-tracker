"""Lance tous les contrôles à la suite. Usage : python3 tout.py"""
import subprocess, sys, os
ICI = os.path.dirname(os.path.abspath(__file__))
for s in ('autotests.py', 'annulation.py', 'cloture.py', 'dates.py', 'injection.py', 'affichage.py'):
    print('\n' + '=' * 20, s)
    r = subprocess.run([sys.executable, os.path.join(ICI, s)], cwd=ICI)
    if r.returncode:
        print('>>> code de sortie', r.returncode)
