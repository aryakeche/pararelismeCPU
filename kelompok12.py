class ILPHazardSimulator:
    def __init__(self):
        self.instructions = []
        
    def add_instruction(self, label, op, dest, src1, src2=None):
        """Menambahkan instruksi: op dest, src1, src2"""
        self.instructions.append({
            "id": len(self.instructions) + 1,
            "label": label,
            "op": op,
            "dest": dest,
            "src1": src1,
            "src2": src2
        })

    def detect_hazards(self):
        hazards = []
        # Melacak penggunaan register: {register: {'last_writer': id, 'readers': [ids]}}
        reg_table = {}

        for i, inst in enumerate(self.instructions):
            i_id = inst['id']
            dest = inst['dest']
            sources = [inst['src1'], inst['src2']] if inst['src2'] else [inst['src1']]

            # 1. Check RAW (Read After Write)
            for src in sources:
                if src in reg_table and reg_table[src]['last_writer'] is not None:
                    writer_id = reg_table[src]['last_writer']
                    if writer_id < i_id:
                        hazards.append({
                            "type": "RAW (Read After Write)",
                            "cause": f"Instruksi {i_id} membaca '{src}' yang ditulis oleh Instruksi {writer_id}",
                            "inst_a": writer_id,
                            "inst_b": i_id
                        })

            # 2. Check WAR (Write After Read): Instruksi j menulis ke register yang dibaca instruksi i sebelumnya
            if dest:
                # Implementasi sederhana pelacakan pembaca aktif
                if dest in reg_table:
                    for reader_id in reg_table[dest]['readers']:
                        if reader_id < i_id:
                            hazards.append({
                                "type": "WAR (Write After Read)",
                                "cause": f"Instruksi {i_id} menulis ke '{dest}' yang sebelumnya dibaca oleh Instruksi {reader_id}",
                                "inst_a": reader_id,
                                "inst_b": i_id
                            })

            # 3. Check WAW (Write After Write): Instruksi j menulis ke register yang ditulis instruksi i sebelumnya
            if dest:
                if dest in reg_table and reg_table[dest]['last_writer'] is not None:
                    writer_id = reg_table[dest]['last_writer']
                    if writer_id < i_id:
                        hazards.append({
                            "type": "WAW (Write After Write)",
                            "cause": f"Instruksi {i_id} menulis ulang '{dest}' yang ditulis oleh Instruksi {writer_id}",
                            "inst_a": writer_id,
                            "inst_b": i_id
                        })

            # Update register table
            if dest not in reg_table:
                reg_table[dest] = {'last_writer': None, 'readers': []}
            
            # Update last writer
            if dest:
                reg_table[dest]['last_writer'] = i_id

            # Update readers
            for src in sources:
                if src:
                    if src not in reg_table:
                        reg_table[src] = {'last_writer': None, 'readers': []}
                    reg_table[src]['readers'].append(i_id)

        return hazards

# --- CONTOH IMPLEMENTASI KASUS HAZARD (RAW, WAR, WAW) ---
simulator = ILPHazardSimulator()

# --- CONTOH IMPLEMENTASI KASUS HAZARD (RAW, WAR, WAW) ---

simulator = ILPHazardSimulator()

print("=== SIMULASI KASUS HAZARD ILP ===")

# I1: Menulis R1, membaca R2 dan R3
simulator.add_instruction("I1", "ADD", "R1", "R2", "R3")

# I2: Membaca R1 yang ditulis I1 -> RAW
simulator.add_instruction("I2", "SUB", "R4", "R1", "R5")

# I3: Menulis ulang R1 yang sebelumnya ditulis I1 -> WAW
# I3 juga menulis R1 setelah I2 membaca R1 -> WAR
simulator.add_instruction("I3", "ADD", "R1", "R6", "R7")

# I4: Menulis R2 yang sebelumnya dibaca I1 -> WAR
simulator.add_instruction("I4", "OR", "R2", "R4", "R1")

# Jalankan deteksi
detected_hazards = simulator.detect_hazards()

for h in detected_hazards:
    print(f"[{h['type']}] -> {h['cause']}")

# Ringkasan
print("\n=== RINGKASAN ===")
for tipe, n in Counter(h['type'] for h in detected_hazards).items():
    print(f"{tipe}: {n}")
print(f"Total hazard: {len(detected_hazards)}")
