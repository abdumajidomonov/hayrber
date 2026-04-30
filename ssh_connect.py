import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('213.199.44.110', username='root', password='Assaqwwq1223', timeout=10)

# Holat tekshirish
stdin, stdout, stderr = client.exec_command('echo ULANDI && hostname && uptime && systemctl is-active odoo')
print(stdout.read().decode())

# SSH public keyni authorized_keys ga qo'shish
with open(r'C:\Users\hacke\.ssh\id_ed25519.pub') as f:
    pub_key = f.read().strip()

cmd = f'mkdir -p ~/.ssh && echo "{pub_key}" > ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh && echo KALIT_QOSHILDI'
stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
print("Ulanish yopildi")
