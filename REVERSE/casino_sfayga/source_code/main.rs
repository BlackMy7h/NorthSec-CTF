use sha2::{Digest, Sha256};
use std::hint::black_box;
use std::io;

// ============================================================================
// BANNER
// ============================================================================

#[allow(dead_code)]
pub fn print_banner() {
    print!(
r#"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$                                                                            $$
$$  Welcome To...                                                             $$
$$   _____  _____  _____  _____  _   _  _____                                 $$
$$  /  __ \|  _  |/  ___||_   _|| \ | ||  _  |                                $$
$$  | /  \/| | | |\ `--.   | |  |  \| || | | |                                $$
$$  | |    | |_| | `--. \  | |  | . ` || | | |                                $$
$$  | \__/\|  _  |/\__/ / _| |_ | |\  |\ \_/ /                                $$
$$   \____/|_| |_|\____/  \___/ \_| \_/ \___/                                 $$
$$                                                                            $$
$$              _____ ______   ___  _   _  _____  ___                         $$
$$             /  ___||  ___| / _ \| | | ||  __ \/ _ \                        $$
$$             \ `--. | |_   / /_\ \ | | || |  \/ /_\ \                       $$
$$              `--. \|  _|  |  _  || | || | __ |  _  |                       $$
$$             /\__/ /| |    | | | || |_| || |_\ \ | | |                      $$
$$             \____/ \_|    \_| |_/\___/  \____/_| |_|                      $$
$$                                                                            $$
$$ ========================================================================== $$
$$                                                                            $$
$$        * * ,;;;;;;;;;,            * * $$
$$    [7][7][7]             ,;;;;;;;;;;;;;             [ $ ]                  $$
$$                        ,;;   _     _   ;;,            |                    $$
$$                       ,;;   (O)   (O)   ;;,         __|__                  $$
$$                       ;;;      | |      ;;;        /_____\                 $$
$$                       ;;;      |_|      ;;;                                $$
$$                       ;;;   [ _|_|_ ]   ;;;    <--[HAHAAAAYOO]              $$
$$                        ';;      ^      ;;'                                 $$
$$                          ';;_________;;'                                   $$
$$                             /       \                                      $$
$$                           //|   |   |\\                                    $$
$$        _______          _// |   |   | \\_          _______                 $$
$$       |   A   |        | |  |   |   | |        |   K   |                    $$
$$       |  <3   |        | |  |___|___|  | |        |   <>  |                $$
$$       |_______|        |_|             |_|        |_______|                $$
$$                                                                            $$
$$                                                                            $$
$$        ___   _      ___     _____  _   _  _____                            $$
$$       / _ \ | |    / _ \   |  _  || \ | ||  ___|                           $$
$$      / /_\ \| |   / /_\ \  | | | ||  \| || |__                             $$
$$      |  _  || |   |  _  |  | | | || . ` ||  __|                            $$
$$      | | | || |___| | | |  \ \_/ /| |\  || |___                            $$
$$      \_| |_/\____/\_| |_/   \___/ \_| \_/\____/                            $$
$$                                                                            $$
$$              ___   _      ___     _____  _    _  _____                     $$
$$             / _ \ | |    / _ \   |_   _|| |  | ||  _  |                    $$
$$            / /_\ \| |   / /_\ \    | |  | |  | || | | |                    $$
$$            |  _  || |   |  _  |    | |  | |/\| || | | |                    $$
$$            | | | || |___| | | |    | |  \  /\  /\ \_/ /                    $$
$$            \_| |_/\____/\_| |_/    \_/   \/  \/  \___/                     $$
$$  remarque: if you bust you restart we love to give second chances          $$
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
"#
    );
}

// ============================================================
// ANTI DEBUG
// ============================================================

fn anti_debug() {
    // Linux-specific anti-debugging check using ptrace
    #[cfg(target_os = "linux")]
    unsafe {
        // PTRACE_TRACEME asks the OS to allow the parent process to trace it.
        // If it's already being traced (e.g., by GDB or another debugger), this fails and returns -1.
        if libc::ptrace(libc::PTRACE_TRACEME, 0, 1, 0) == -1 {
            println!("[!] baghi tdebuggi zaama ?"); // Mocking message for debuggers
            std::process::exit(0);
        }
    }
}

// ============================================================
// HISTORY (UNCHANGED)
// ============================================================

#[derive(Clone)]
struct History {
    mask: u64,
    ops: u64,
}

impl History {
    fn new() -> Self {
        Self {
            mask: 0xA5A5_F00D_CAFE_BEEF, // Magic initial mask
            ops: 0,
        }
    }

    // Records an operation (like hit/stand) into the history mask
    fn push(&mut self, v: u8) {
        self.ops += 1;
        // Shift the input value by a rotating modulo amount based on operation count
        self.mask ^= (v as u64) << (self.ops % 57);
        // Scramble the mask using a large prime multiplier
        self.mask = self.mask.wrapping_mul(0x9E37_79B9_7F4A_7C15);
    }

    // Creates the final history hash to be used for state unlock
    fn finalize(&self) -> u64 {
        // XOR mask with scrambled ops counter
        let mut x = self.mask ^ self.ops.wrapping_mul(0x1337);

        // Mix the hash using shifts and large prime multiplications
        x ^= x >> 33;
        x = x.wrapping_mul(0xff51afd7ed558ccd);
        x ^= x >> 33;

        x ^= x >> 29;
        x = x.wrapping_mul(0x94d049bb133111eb);
        x ^= x >> 32;

        x
    }
}

// ============================================================
// CASINO (UNCHANGED CORE)
// ============================================================

struct Casino {
    rounds: u64,
    hits: u64,
    busts: u64,
    rng: u64,
    player: u32,
    dealer: u32,
    history: History,
    hidden: u64,
}

impl Casino {
    fn new() -> Self {
        Self {
            rounds: 0,
            hits: 0,
            busts: 0,
            rng: 0x9e3779b97f4a7c15, // LCG / Xorshift initial seed
            player: 0,
            dealer: 0,
            history: History::new(),
            hidden: 0xD1CEB00B_F00D_C0DE, // Initial hidden state
        }
    }

    // Custom RNG implementation (Xorshift variant)
    fn next(&mut self) -> u32 {
        let mut x = self.rng;
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        self.rng = x;
        // Output scrambling
        (x.wrapping_mul(0x2545F4914F6CDD1D) >> 32) as u32
    }

    // Deal cards (value between 12 and 21)
    fn deal(&mut self) -> u32 {
        (self.next() % 10) + 12
    }

    // Draw card (value between 1 and 10)
    fn draw(&mut self) -> u32 {
        (self.next() % 10) + 1
    }

    // Main game logic for a single round
    fn round(&mut self) {
        self.rounds += 1;

        self.player = self.deal();
        self.dealer = self.deal();

        loop {
            // Note: Dealer's score is halved visually to obscure exact values
            println!("Player: {} | Dealer: {}", self.player, self.dealer / 2);
            println!("(h)it (s)tand (q)uit");

            let mut i = String::new();
            io::stdin().read_line(&mut i).unwrap();
            let c = i.trim();

            if c == "q" {
                std::process::exit(0);
            }

            if c == "h" {
                // Hitting pushes '1' to history
                self.history.push(1);
                self.hits += 1;
                self.player += self.draw();

                if self.player > 21 {
                    // Busting pushes '0' to history
                    self.history.push(0);
                    self.busts += 1;
                    return; // End round immediately
                }
            } else {
                // Standing pushes '0' to history
                self.history.push(0);
                break;
            }
        }

        // Complex mutation of hidden state based on player score, rounds, and hits
        self.hidden ^= (self.player as u64)
            .wrapping_add(self.rounds << 3)
            .rotate_left((self.hits % 16) as u32);

        self.hidden = self.hidden.wrapping_mul(0x9E37_79B9_7F4A_7C15);

        // Dealer logic to automatically beat player if possible
        if self.player > self.dealer {
            self.dealer = self.player + 1;
        }
    }

    // Win condition / state unlock trigger
    // Requires more than 6 rounds, at least 3 busts, and a specific magic history hash ending in 0x42
    fn trigger(&self) -> bool {
        self.rounds > 6
            && self.busts >= 3
            && (self.history.finalize() & 0xFF) == 0x42
    }
}

// ============================================================
// UNPACKER (🔥 STATE-COUPLED VERSION)
// ============================================================

// Unpacks the base bytecode using an initial state seed
fn unpack(mut state: u32) -> Vec<u8> {
    let base = vec![
        0x11,0x22,0x33,0x44,0xAA,
        0x55,0x66,0x77,0x88,0x99,
        0xAB,0xCD,0xEF,0x13,0x37,
    ];

    let mut code = vec![0u8; base.len()];
    let mut prev: u8 = 0xC3; // Chaining variable
    let mut t: u32 = 0xC0FFEE12; // Scrambling constant

    for i in 0..base.len() {
        // Mutate unpacking state
        state ^= state.wrapping_mul(0x6D2B79F5);
        state ^= state.rotate_left(11).wrapping_add(t);

        // Mutate scrambling constant based on state and index
        t = t.wrapping_mul(0x45D9F3B)
            ^ state.rotate_right((i as u32) & 31);

        // Derive key byte for current instruction decryption
        let key = ((state ^ t ^ (prev as u32)) >> ((i % 5) + 3)) as u8;
        
        let idx = i as u8;
        
        let base_b: u8 = base[i];
        let key_u8 = key as u8;
        
        // Decrypt current bytecode instruction
        let mut b = base_b
            .wrapping_add(idx)
            ^ key
            ^ prev;

        // Update chaining variable for the next iteration
        prev = b.rotate_left((state % 7) as u32) ^ (t as u8);

        code[i] = b;
    }

    code
}

// ============================================================
// VM (🔥 HARDENED ORDER-DEPENDENT VERSION)
// ============================================================

struct VM {
    regs: [u32; 8],        // 8 general purpose registers
    state: u32,            // VM master state
    trace: u32,            // Execution trace to prevent instruction skipping
    pc: usize,             // Program counter
    code: Vec<u8>,         // Unpacked bytecode
    fingerprint: u32,      // Execution fingerprint

    // 🔥 anti-emulation additions
    last_op: u8,
    stall: u32,
    exec_noise: u8,
}

impl VM {
    fn new(state: u32) -> Self {
        Self {
            regs: [0; 8],
            state,
            trace: 0,
            pc: 0,
            code: unpack(state),
            fingerprint: 0x1337C0DE,

            last_op: 0,
            stall: 0,
            exec_noise: 0x5A,
        }
    }

    fn step(&mut self) {
        // ====================================================
        // EXECUTION-ORDER DEPENDENT FETCH (CRITICAL)
        // ====================================================

        // Fetch op-code, loop around if PC exceeds code length
        let mut op = self.code[self.pc % self.code.len()];
        
        // Decrypt op-code dynamically based on current VM state and noise
        op ^= self.state as u8;
        op ^= self.exec_noise; // 🔥 breaks static emulation tools

        self.pc += 1;

        // ====================================================
        // READ-AFTER-WRITE DEPENDENCY (TIMING ATTACK STYLE)
        // ====================================================

        // If the same opcode is executed sequentially, introduce complex stalling mutations
        // This ensures timing/execution order is strictly preserved.
        if self.last_op == op {
            self.stall ^= self.trace;
            self.state ^= self.stall.rotate_left(3);
        }

        // ====================================================
        // ORIGINAL VM LOGIC
        // ====================================================

        match op {
            0x11 => self.regs[0] ^= self.regs[1],
            0x22 => self.regs[1] = self.regs[1].wrapping_add(3),
            0x33 => self.regs[2] ^= 0x1337,
            0x44 => self.regs[3] = self.regs[3].wrapping_mul(3),
            0x55 => self.regs[4] = self.regs[4].rotate_left(1),

            0x66 => {
                // Conditional mutation based on trace and stall
                if self.trace.wrapping_add(self.stall) & 3 == 0 {
                    self.regs[5] ^= self.trace ^ self.state;
                } else {
                    self.regs[5] ^= self.trace.rotate_left(1);
                }
            }

            0x77 => self.regs[6] = self.regs[6].wrapping_add(self.state),
            0x88 => self.regs[7] ^= self.regs[0],

            0xAA => {
                if self.trace & 1 == 0 {
                    self.regs[0] ^= 0xDEADBEEF;
                }
            }

            _ => {} // NOP or unrecognized instruction
        }

        self.last_op = op;

        // ====================================================
        // INTERNAL STATE EVOLUTION
        // ====================================================

        // Trace updates based on the operation performed
        self.trace = self.trace.rotate_left(5) ^ op as u32;

        // Bytecode itself mutates after every execution (Self-Modifying Code)
        let idx = (self.state as usize) % self.code.len();
        self.code[idx] ^= op.wrapping_add(self.trace as u8);

        // State mutates based on the execution trace
        self.state ^= self.trace;
        self.state = self.state.rotate_right(3);

        // Noise update for next opcode fetch decryption
        self.exec_noise = self.exec_noise.wrapping_mul(31) ^ (self.trace as u8);

        // Fingerprint update
        self.fingerprint ^= self.trace.rotate_left(self.pc as u32);
        self.fingerprint = self.fingerprint.wrapping_mul(0x45d9f3b);
    }

    // Runs a dynamic number of steps based on the initial state
    fn run(&mut self) {
        let steps = 64 + (self.state & 31);
        for _ in 0..steps {
            self.step();
        }
    }

    // Derives a final decryption key array using SHA-256 over the complete internal VM state
    fn key(&self, history: u64, game_seed: u32) -> [u8; 32] {
        let mut h = Sha256::new();

        // Feed all registers
        for r in &self.regs {
            h.update(r.to_le_bytes());
        }

        // Feed VM state properties
        h.update(self.state.to_le_bytes());
        h.update(self.trace.to_le_bytes());
        
        // Feed casino properties
        h.update(history.to_le_bytes());
        h.update(game_seed.to_le_bytes());
        
        // Feed execution fingerprint
        h.update(self.fingerprint.to_le_bytes());

        // Finalize hash
        h.finalize().into()
    }
}

// ============================================================
// ENCRYPTED FLAG (UNCHANGED)
// ============================================================

// The payload that needs to be decrypted
const ENC: &[u8] = &[
    0x72, 0x4d, 0x9c, 0xea, 0x30, 0xf8, 0x5b, 0x89,
    0x40, 0x70, 0x6d, 0x54, 0x0f, 0x1c, 0xd4, 0x9e,
    0xb6, 0x01, 0xe7, 0xc9, 0xfc, 0xaf, 0x9f, 0xe1,
    0x30, 0x4a, 0x14, 0x25, 0xb4, 0xe0, 0xd7, 0x91,
    0x63, 0x6c, 0xec, 0xe7, 0x4d, 0xb9, 0x5b, 0x8e,
    0x46, 0x70, 0x34, 0x50, 0x57, 0x51, 0xd0, 0xb5,
    0x94,
];

// ============================================================
// MAIN (UNCHANGED LOGIC)
// ============================================================

fn main() {
    print_banner();
    anti_debug();

    let mut game = Casino::new();

    loop {
        // Run casino logic continuously
        game.round();

        // Check if the specific set of actions was performed to trigger the unlock
        if game.trigger() {
            println!("[*] unlocked state");

            // Derive initialization seed based on all casino actions taken
            let mut h = Sha256::new();
            h.update(game.rounds.to_le_bytes());
            h.update(game.hits.to_le_bytes());
            h.update(game.busts.to_le_bytes());
            h.update(game.history.finalize().to_le_bytes());
            h.update(game.hidden.to_le_bytes());

            let mut init_bytes = h.finalize();
            // Take first 4 bytes of hash as initial 32-bit state
            let mut init = u32::from_le_bytes(init_bytes[0..4].try_into().unwrap());

            // Scramble the initialization seed
            init ^= init.rotate_left(11);
            init = init.wrapping_mul(0x9E3779B1);
            init ^= init >> 16;
            init = init.rotate_left((game.busts % 32) as u32);

            // Prevent compiler from optimizing away the init value
            black_box(init);

            // Instantiate custom VM and execute it
            let mut vm = VM::new(init);
            vm.run();

            // Fetch final history and use VM state to construct the decryption key
            let history = game.history.finalize();
            let key = vm.key(history, init);

            // XOR decrypt the ENC array using the derived key
            let out: Vec<u8> = ENC.iter()
                .enumerate()
                .map(|(i, b)| b ^ key[i % 32])
                .collect();

            // Check if decryption succeeded (looks for standard flag prefix)
            if out.starts_with(b"NSC{") {
                println!("waa rbahatoo: {}", String::from_utf8_lossy(&out));
            } else {
                println!("marra jaya inchaallah");
            }

            break; // Exit loop after unlocking attempt
        }
    }
}