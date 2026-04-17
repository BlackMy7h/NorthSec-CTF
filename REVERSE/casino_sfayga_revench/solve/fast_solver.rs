use std::fs::File;
use std::io::Write;

const MULTIPLIER: u64 = 0x9E37_79B9_7F4A_7C15;
const RNG_MULT: u64 = 0x2545F4914F6CDD1D;
const TARGET_HASH: u32 = 0x1337C0DE;

#[inline(always)]
fn push(mask: &mut u64, ops: &mut u64, action: u8, value: u32) {
    *ops += 1;
    let combo = ((action as u64) << 32) | (value as u64);
    *mask ^= combo.rotate_left((*ops % 61) as u32);
    *mask = mask.wrapping_mul(MULTIPLIER);
    *mask ^= *mask >> 31;
}

#[inline(always)]
fn finalize(mask: u64, ops: u64) -> u32 {
    let mut x = mask ^ ops.wrapping_mul(0x1337BEEF);
    x ^= x >> 33;
    x = x.wrapping_mul(0xff51afd7ed558ccd);
    x ^= x >> 33;
    x = x.wrapping_mul(0xc4ceb9fe1a85ec53);
    x ^= x >> 33;
    (x & 0xFFFFFFFF) as u32
}

struct Solver {
    count: u64,
}

impl Solver {
    fn solve(
        &mut self,
        rng: u64,
        mask: u64,
        ops: u64,
        rounds: u64,
        busts: u64,
        max_rounds: u64,
        path: &mut String,
    ) -> bool {
        self.count += 1;
        if self.count % 100_000_000 == 0 {
            println!("[*] Explored {}00 million states...", self.count / 100_000_000);
        }

        if rounds > 6 && busts >= 3 {
            if finalize(mask, ops) == TARGET_HASH {
                return true;
            }
        }

        if rounds >= max_rounds {
            return false;
        }

        let mut next_rng = rng;
        
        // Round start
        let mut r_rng = next_rng;
        let mut r_next = |rng: &mut u64| {
            let mut x = *rng;
            x ^= x >> 12;
            x ^= x << 25;
            x ^= x >> 27;
            *rng = x;
            (x.wrapping_mul(RNG_MULT) >> 32) as u32
        };

        let p_card = (r_next(&mut r_rng) % 10) + 12;
        let d_card = (r_next(&mut r_rng) % 10) + 12;

        let mut base_mask = mask;
        let mut base_ops = ops;
        push(&mut base_mask, &mut base_ops, 1, p_card);
        push(&mut base_mask, &mut base_ops, 1, d_card);

        let mut current_player = p_card;
        let mut current_mask = base_mask;
        let mut current_ops = base_ops;
        let mut current_rng = r_rng;
        let mut hits = 0;

        loop {
            // Option: Stand
            if current_player <= 21 {
                let mut s_mask = current_mask;
                let mut s_ops = current_ops;
                push(&mut s_mask, &mut s_ops, 3, current_player);
                
                path.push('s');
                path.push('\n');
                if self.solve(current_rng, s_mask, s_ops, rounds + 1, busts, max_rounds, path) {
                    return true;
                }
                path.truncate(path.len() - 2);
            } else {
                // Option: Bust
                let mut b_mask = current_mask;
                let mut b_ops = current_ops;
                push(&mut b_mask, &mut b_ops, 4, current_player);
                
                // path already has the 'h\n's
                if self.solve(current_rng, b_mask, b_ops, rounds + 1, busts + 1, max_rounds, path) {
                    return true;
                }
                break;
            }

            // Option: Hit
            let card = (r_next(&mut current_rng) % 10) + 1;
            current_player += card;
            push(&mut current_mask, &mut current_ops, 2, card);
            path.push('h');
            path.push('\n');
            hits += 1;
        }

        // Backtrack 'h\n's
        path.truncate(path.len() - hits * 2);
        false
    }
}

fn main() {
    let mut solver = Solver { count: 0 };
    for max_r in 7..=25 {
        println!("[*] Searching with max_rounds = {}...", max_r);
        let mut path = String::new();
        if solver.solve(
            0x9e3779b97f4a7c15,
            0xA5A5_F00D_CAFE_BEEF,
            0,
            0,
            0,
            max_r,
            &mut path,
        ) {
            println!("[+] Found solution!");
            println!("{}", path);
            let mut f = File::create("solution.txt").unwrap();
            f.write_all(path.as_bytes()).unwrap();
            return;
        }
    }
}
