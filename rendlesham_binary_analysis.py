"""
Rendlesham Forest Incident — Binary Code Analysis
==================================================
Source: Jim Penniston's notebook binary (Simon_Format transcription)
        2210_Compilation_Binary_Corrected — final screened source
        (one flipped bit + 5 scaffolding additions for XOR analysis)

Public Source:
  https://www.therendleshamforestincident.com/2022/04/
  2010-it-was-revealed-by-jim-penniston.html?m=1

Analyses implemented:
  1. XOR Analysis      — pairwise XOR between pages; torus XOR (page 1 ↔ page 14)
  2. Stacking          — vertical column-wise bit analysis across all pages
  3. 64-bit Analysis   — break each page into 64-bit words, hex/decimal/ASCII decode
  4. Torus Mapping     — pages arranged on a toroidal surface (page 1 → page 14 wrap)
"""

import textwrap
import itertools
from collections import Counter

# ──────────────────────────────────────────────────────────────────────────────
# RAW DATA — Simon_Format, Pages 1–14
# Extracted from: 2210_Compilation_Binary_Corrected.xlsx (Simon_Format sheet)
# Null/space separators between groups preserved as '|' in SEGMENTED form.
# FULL form strips separators for continuous bit-stream analysis.
# ──────────────────────────────────────────────────────────────────────────────

PAGES_FULL = [
    # Page 1  (245 bits)
    "01000101010110000011010100110010010101010011110101010001100100111010101001001010"
    "011001001101100011001101110110010001101110011100000110001001101001100100011010100"
    "11000110111001100000110010001110000100010101011001010011110101001001001111010100"
    "1001",

    # Page 2  (219 bits)
    "01010000010011000011000000110010011010101010011011010101001001001010101110011011"
    "000110011010011100011000100110011001100110111001100000000110110001111100110001100"
    "1100010011001100010100001000101010010010100011100100101000",

    # Page 3  (192 bits)
    "01001111010100100100001100100011010001100100111000100100001000011001100010011010"
    "011000100110001011001001100010011010100100000110011000000000000110001101010100110"
    "1001001010011101110100100101001",

    # Page 4  (199 bits)
    "01000101010101000010100110011001101100100101000001000100111101001111010011001101"
    "111010011100000111000110011110000001101010100001111000000110011100100101001111010"
    "0011000110101001100101110010110010 1000",

    # Page 5  (196 bits)
    "10010010100111101000010010011101100010000101000100010010010100111100011100000111"
    "010000110000110001001101010011001101110101010110001110101010011101011001010011101"
    "00110000001110011010100000101010011",

    # Page 6  (197 bits)
    "11100100111101000001100100110011001110010001010101011100100000101010100110010011"
    "000111011010100110001001100110011010100110001000111000110011000110010010101010100"
    "100011010000110010100011100000110011",

    # Page 7  (187 bits)
    "11101001000010101110001001100110001000001010101000101010000110100011000100110011"
    "000110110011000100110110110011011100001100001001000101000110101010001010101100101"
    "00110101001100110100110000",

    # Page 8  (177 bits)
    "01010011010100000100110001001100100011001001011001011110100110010101110011011100"
    "110101011100110011000110100110000011010000100110110011001100110010000101000110010"
    "0100111000110000",

    # Page 9  (135 bits)
    "01001110010010010110001100101010100000101000100010010010100111001100011101000111"
    "00100111001010000110011000110111001110100110011000100 11",

    # Page 10  (126 bits)
    "01010100010110010111010000110100100010101100100101010101001101010000010101110011"
    "10010011010101011100110011001000110011001100 01",

    # Page 11  (94 bits)
    "001101100110111111010011100000101001110100010101010100000110011001110111001101100"
    "0001100110011",

    # Page 12  (70 bits)
    "0011011001110000101010001000001110010001010100111001000011100000010011",

    # Page 13  (79 bits)
    "0011000100110000100100101001110100100001010000110110001010011000000001000110110",

    # Page 14  (52 bits)
    "0011000001010000010100111000000110010011100101010111",
]

PAGES_SEGMENTED = [
    # Page 1
    ["01000101","01011000","00110101","00110010","01010101001111","01","01",
     "0100011001001110101010","0100101","001100100110110","0011","00110111",
     "0110010","00110111","00111000","0011000100110100","11001000110101","0",
     "0110","001101110011000","00110010","00111000","0100","010101011001",
     "01001111","01010010","01001111","01010010","01"],
    # Page 2
    ["01010000","01001100","00110000","00110010011","0101","0101","001101",
     "10101010010010010101","01110011011000110011","010011100011","0001",
     "001100110011","001101110011000000","001101100011","111","00110001",
     "1001100010011","00110001","01000","01000","101","01001001","01000111",
     "001001","0","1000"],
    # Page 3
    ["01001111","01010010","0100001100100011","01000110","0100111",
     "000100100001000011","00110001","001101","00110001","00110001","0110",
     "0100","11000","10011010100","10000011","0011000000","000000110001",
     "101","01010011","01001001","01001110","111","01001001","01001"],
    # Page 4
    ["01000101","010101000","0101001100110011","0110010010100000100",
     "01001111010011110100","1100110111","101","00111","00000","1110",
     "00110011","110000","00110101","01000011","110000","0011",
     "00111001001","0100111101000110","00110101","00110010","1110","0101100101000"],
    # Page 5
    ["1001001010011110100","0010","01001110","110001000010100",
     "01000100100101001","111000111000001","11010000","1100","001100010011",
     "010100","1100110111","0101","01","0110","0011","101010100111",
     "01011001010011101","00110000","00111001","1010100000","101010011"],
    # Page 6
    ["1110","01001111","01000","00110010011001100","1110","01000101010101",
     "1100100000101010100","11001","00110001","1101101010011","0001",
     "00110011","00110101001100010","001110","0011","0011","000110010",
     "01010101010010","00110100","00110010","10001110000","01100","11"],
    # Page 7
    ["111","01001000","010101","110001","00110011","00010000010101",
     "0100010101000011010","00110001","00110","01100011011","0011","0001",
     "0011","0110110011011100","001100","0010","010001010","00110101",
     "010001010101100101","00110101","00110011","01","00110000"],
    # Page 8
    ["010100110101000001","00110001001100100011","0010","01011001",
     "01111010011001010","111001101110011","01010111","00110","0110",
     "00110100","11000","00110","1000","010011","0110011","00110011001",
     "000","0","1010","00110010","01001110","00110000"],
    # Page 9
    ["01001110","01001001","0110","0011001","0101","01000001","01000",
     "1000100100101001110","0110","00111","01000111","001","00111",
     "00101000","0110011","0001","101110011","1010011","00110001","0011"],
    # Page 10
    ["01010100","01011001","0111","01000011","0100","10001010110010",
     "010101010100","1101010","000","01010111","00111001","001","101",
     "0101011100110011","0010","00110011","00110001"],
    # Page 11
    ["0011011","0011011","111101001110","0000101001110","1000101010101000",
     "001100110011","10111","00110110","00","00110011","0011"],
    # Page 12
    ["0011011","00111000","01010100","0100","000111001000","10101001110",
     "0100","00111000","0001","0011"],
    # Page 13
    ["00110001","00110000","100100101001110","100","100001",
     "01000011011000101","0011000000","0010","00110110"],
    # Page 14
    ["00110000","010100000101001","11000000110010","011100","101010111"],
]

# Strip any spaces accidentally left in (from copy) 
PAGES_FULL = [''.join(p.split()) for p in PAGES_FULL]

NUM_PAGES = len(PAGES_FULL)
MAX_BITS  = max(len(p) for p in PAGES_FULL)


# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def pad_page(bits: str, length: int, pad: str = "0") -> str:
    """Right-pad a bit string to a given length."""
    return bits.ljust(length, pad)


def bits_to_int(bits: str) -> int:
    return int(bits, 2) if bits else 0


def bits_to_hex(bits: str) -> str:
    n = len(bits)
    padded = bits.ljust((n + 3) // 4 * 4, "0")
    value = int(padded, 2)
    hex_digits = len(padded) // 4
    return f"0x{value:0{hex_digits}X}"


def bits_to_ascii(bits: str) -> str:
    """Decode bit string as 8-bit ASCII, replacing non-printable chars with '.'"""
    result = ""
    for i in range(0, len(bits) - 7, 8):
        code = int(bits[i:i+8], 2)
        result += chr(code) if 32 <= code < 127 else "."
    return result


def xor_bits(a: str, b: str) -> str:
    """XOR two bit strings (shortest length wins)."""
    length = min(len(a), len(b))
    return "".join("0" if a[i] == b[i] else "1" for i in range(length))


def count_ones(bits: str) -> int:
    return bits.count("1")


def bit_density(bits: str) -> float:
    return count_ones(bits) / len(bits) if bits else 0.0


def wrap_index(i: int, total: int) -> int:
    """Toroidal wrap: index i within [0, total)."""
    return i % total


def section(title: str, width: int = 78) -> None:
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def subsection(title: str) -> None:
    print(f"\n--- {title} ---")


# ──────────────────────────────────────────────────────────────────────────────
# 1. XOR ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

def xor_analysis():
    section("1. XOR ANALYSIS")
    print(
        "XOR reveals bit-position differences between pages.\n"
        "A '1' in the XOR result means the two pages DIFFER at that position.\n"
        "A '0' means they AGREE."
    )

    # 1a — Sequential pairwise XOR (page N vs page N+1, torus-wrapped)
    subsection("1a. Sequential pairwise XOR (page N ⊕ page N+1), torus-wrapped")
    print(f"{'Pair':<14} {'Bits compared':<15} {'Differences':<13} {'% differ':<10} XOR (first 64 bits)")
    print("-" * 78)
    for i in range(NUM_PAGES):
        j = wrap_index(i + 1, NUM_PAGES)
        a = PAGES_FULL[i]
        b = PAGES_FULL[j]
        result = xor_bits(a, b)
        diffs = count_ones(result)
        pct = 100.0 * diffs / len(result)
        label = f"P{i+1:02d} ⊕ P{j+1:02d}"
        print(f"{label:<14} {len(result):<15} {diffs:<13} {pct:<10.2f} {result[:64]}")

    # 1b — Torus boundary XOR: page 1 ⊕ page 14 (the wrap-around edge)
    subsection("1b. Torus boundary XOR: Page 1 ⊕ Page 14 (wrap-around)")
    a, b = PAGES_FULL[0], PAGES_FULL[-1]
    result = xor_bits(a, b)
    diffs = count_ones(result)
    print(f"  Page 1  ({len(a):>3} bits): {a[:64]}...")
    print(f"  Page 14 ({len(b):>3} bits): {b[:64]}...")
    print(f"  XOR     ({len(result):>3} bits): {result[:64]}...")
    print(f"  Differing bits: {diffs} / {len(result)}  ({100.0*diffs/len(result):.2f}%)")

    # 1c — All-pairs XOR heatmap summary
    subsection("1c. All-pairs XOR difference heatmap (% bits differing)")
    header = "     " + "".join(f"P{j+1:02d} " for j in range(NUM_PAGES))
    print(header)
    for i in range(NUM_PAGES):
        row_str = f"P{i+1:02d}  "
        for j in range(NUM_PAGES):
            if i == j:
                row_str += " --  "
            else:
                xr = xor_bits(PAGES_FULL[i], PAGES_FULL[j])
                pct = 100.0 * count_ones(xr) / len(xr)
                row_str += f"{pct:4.0f} "
        print(row_str)

    # 1d — Self-XOR with cyclic shift (find repeating bit patterns)
    subsection("1d. Page 1 self-XOR at cyclic shifts (first 20 shifts)")
    p1 = PAGES_FULL[0]
    print(f"  Shift  Differences  % differ  (of {len(p1)} bits)")
    for shift in range(1, 21):
        shifted = p1[shift:] + p1[:shift]
        r = xor_bits(p1, shifted)
        d = count_ones(r)
        print(f"  {shift:>5}  {d:>11}  {100.0*d/len(r):>8.2f}%")


# ──────────────────────────────────────────────────────────────────────────────
# 2. STACKING ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

def stacking_analysis():
    section("2. STACKING ANALYSIS")
    print(
        "All 14 pages are aligned and stacked into a 2D grid (page × bit-position).\n"
        "Analysis examines each BIT COLUMN across all pages."
    )

    # Pad all pages to MAX_BITS
    matrix = [pad_page(p, MAX_BITS, "0") for p in PAGES_FULL]

    # 2a — Column sums (how many pages have a '1' at each bit position)
    subsection("2a. Column sums (count of '1' at each bit position across 14 pages)")
    col_sums = []
    for col in range(MAX_BITS):
        s = sum(1 for row in matrix if row[col] == "1")
        col_sums.append(s)

    # Distribution of column sums
    dist = Counter(col_sums)
    print("  Column sum → count of bit positions with that many '1's:")
    for k in sorted(dist.keys()):
        bar = "█" * dist[k]
        print(f"    {k:>2} ones in column: {dist[k]:>4} positions  {bar}")

    # Find constant-1 and constant-0 columns
    all_ones  = [i for i, s in enumerate(col_sums) if s == NUM_PAGES]
    all_zeros = [i for i, s in enumerate(col_sums) if s == 0]
    print(f"\n  Bit positions where ALL 14 pages agree on '1': {len(all_ones)}")
    if all_ones:
        print(f"    Positions: {all_ones[:30]}{'...' if len(all_ones)>30 else ''}")
    print(f"  Bit positions where ALL 14 pages agree on '0': {len(all_zeros)}")
    if all_zeros:
        print(f"    Positions: {all_zeros[:30]}{'...' if len(all_zeros)>30 else ''}")

    # 2b — Row (page) bit density
    subsection("2b. Per-page bit density (proportion of '1' bits)")
    print(f"  {'Page':<8} {'Bits':<8} {'Ones':<8} {'Density':>8}")
    print(f"  {'-'*36}")
    for i, p in enumerate(PAGES_FULL):
        ones = count_ones(p)
        dens = bit_density(p)
        bar = "█" * int(dens * 40)
        print(f"  P{i+1:02d}     {len(p):<8} {ones:<8} {dens:>8.3f}  {bar}")

    # 2c — Stacked majority bit string
    subsection("2c. Majority-vote bit string (most common bit at each column)")
    majority = ""
    for col in range(MAX_BITS):
        ones = col_sums[col]
        zeros = NUM_PAGES - ones
        majority += "1" if ones >= zeros else "0"
    print(f"  Majority string ({len(majority)} bits):")
    for i in range(0, min(len(majority), 256), 64):
        print(f"    {majority[i:i+64]}")
    print(f"  ASCII decode of majority string: {bits_to_ascii(majority)}")

    # 2d — Stacked XOR across all pages (cumulative XOR)
    subsection("2d. Cumulative XOR across all pages (P1 ⊕ P2 ⊕ ... ⊕ P14)")
    cumxor = pad_page(PAGES_FULL[0], MAX_BITS)
    for p in PAGES_FULL[1:]:
        pb = pad_page(p, MAX_BITS)
        cumxor = xor_bits(cumxor, pb)
    print(f"  Cumulative XOR ({len(cumxor)} bits):")
    for i in range(0, min(len(cumxor), 256), 64):
        print(f"    {cumxor[i:i+64]}")
    print(f"  Ones in cumulative XOR: {count_ones(cumxor)} ({bit_density(cumxor):.3f})")
    print(f"  ASCII decode: {bits_to_ascii(cumxor)}")


# ──────────────────────────────────────────────────────────────────────────────
# 3. 64-BIT ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

def analysis_64bit():
    section("3. 64-BIT WORD ANALYSIS")
    print(
        "Each page is split into 64-bit words.\n"
        "Each word is shown as: binary | hexadecimal | decimal | ASCII (8 chars)"
    )

    # Build a flat stream from all pages concatenated
    full_stream = "".join(PAGES_FULL)
    print(f"\n  Total bits in full stream: {len(full_stream)}")
    print(f"  Full 64-bit words: {len(full_stream) // 64}")
    print(f"  Leftover bits: {len(full_stream) % 64}")

    # 3a — Per-page 64-bit breakdown
    for page_idx, bits in enumerate(PAGES_FULL):
        subsection(f"3a. Page {page_idx+1} ({len(bits)} bits) → {len(bits)//64} full 64-bit words")
        if len(bits) < 64:
            print(f"  (Page too short for a full 64-bit word — raw bits: {bits})")
            print(f"  Hex: {bits_to_hex(bits)}")
            continue
        for w in range(len(bits) // 64):
            word = bits[w*64:(w+1)*64]
            val  = bits_to_int(word)
            asc  = "".join(
                chr(int(word[k:k+8], 2)) if 32 <= int(word[k:k+8], 2) < 127 else "."
                for k in range(0, 64, 8)
            )
            print(f"  Word {w+1}: {word}")
            print(f"         Hex: {val:#018x}  Dec: {val:<22}  ASCII: [{asc}]")
        # Remainder
        rem = bits[len(bits) - (len(bits) % 64):]
        if rem:
            print(f"  Remainder ({len(rem)} bits): {rem} → Hex: {bits_to_hex(rem)}")

    # 3b — Full-stream 64-bit words
    subsection("3b. Full concatenated stream — all 64-bit words")
    print(f"  {'Word':>5}  {'Hex':<20}  {'Dec':<22}  ASCII")
    print(f"  {'-'*70}")
    for w in range(len(full_stream) // 64):
        word = full_stream[w*64:(w+1)*64]
        val  = bits_to_int(word)
        asc  = "".join(
            chr(int(word[k:k+8], 2)) if 32 <= int(word[k:k+8], 2) < 127 else "."
            for k in range(0, 64, 8)
        )
        print(f"  {w+1:>5}  {val:#018x}  {val:<22}  [{asc}]")

    # 3c — XOR of all 64-bit words (full stream)
    subsection("3c. XOR of all 64-bit words in full stream")
    words = [full_stream[w*64:(w+1)*64] for w in range(len(full_stream)//64)]
    if words:
        acc = words[0]
        for word in words[1:]:
            acc = xor_bits(acc, word)
        val = bits_to_int(acc)
        asc = "".join(
            chr(int(acc[k:k+8], 2)) if 32 <= int(acc[k:k+8], 2) < 127 else "."
            for k in range(0, 64, 8)
        )
        print(f"  XOR of all {len(words)} words:")
        print(f"    Binary: {acc}")
        print(f"    Hex:    {val:#018x}")
        print(f"    Dec:    {val}")
        print(f"    ASCII:  [{asc}]")


# ──────────────────────────────────────────────────────────────────────────────
# 4. TORUS ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

def torus_analysis():
    section("4. TORUS ANALYSIS  (Page 1 ↔ Page 14 wrap-around)")
    print(
        "The 14 pages are mapped onto a torus surface:\n"
        "  • One axis = page number  (wraps: Page 1 follows Page 14)\n"
        "  • Other axis = bit position within page  (wraps at page length)\n"
        "\n"
        "This models the hypothesis that the binary is cyclic — the end of\n"
        "the last page connects back to the start of the first page."
    )

    # 4a — Torus coordinates for every bit
    subsection("4a. Torus coordinate mapping — first 60 bits (sample)")
    print(f"  {'Bit#':<7} {'Page':<6} {'Bit-in-page':<14} {'Value':<7} Torus(page,bit)")
    print(f"  {'-'*55}")
    global_bit = 0
    shown = 0
    for page_idx, bits in enumerate(PAGES_FULL):
        for bit_pos, b in enumerate(bits):
            torus_page = wrap_index(page_idx, NUM_PAGES)
            torus_bit  = wrap_index(bit_pos,  len(bits))
            if shown < 60:
                print(f"  {global_bit:<7} {page_idx+1:<6} {bit_pos:<14} {b:<7} ({torus_page+1}, {torus_bit})")
                shown += 1
            global_bit += 1
    print(f"  ... (total {global_bit} bits mapped)")

    # 4b — Torus adjacency: for each bit, compare with its 4 torus neighbours
    subsection("4b. Torus adjacency analysis — neighbour agreement per page")
    print(
        "  For each bit at (page p, position b), its 4 torus neighbours are:\n"
        "    LEFT  = (p, b-1), RIGHT = (p, b+1),\n"
        "    UP    = (p-1, b), DOWN  = (p+1, b)  [all indices wrapped]\n"
    )
    padded = [pad_page(p, MAX_BITS, "0") for p in PAGES_FULL]

    total_bits = sum(len(p) for p in PAGES_FULL)
    total_agreements = 0
    per_page_agree = []

    for pi in range(NUM_PAGES):
        page_agree = 0
        page_len = len(PAGES_FULL[pi])
        for bi in range(page_len):
            centre = padded[pi][bi]
            left   = padded[pi][wrap_index(bi - 1, page_len)]
            right  = padded[pi][wrap_index(bi + 1, page_len)]
            up     = padded[wrap_index(pi - 1, NUM_PAGES)][bi]
            down   = padded[wrap_index(pi + 1, NUM_PAGES)][bi]
            agrees = sum(1 for n in [left, right, up, down] if n == centre)
            page_agree += agrees
        per_page_agree.append(page_agree)
        total_agreements += page_agree

    max_possible = sum(len(p) * 4 for p in PAGES_FULL)
    print(f"  {'Page':<8} {'Bits':<8} {'Agreements':<14} {'/ Max':<10} {'%':>6}")
    print(f"  {'-'*50}")
    for pi in range(NUM_PAGES):
        bits = len(PAGES_FULL[pi])
        mx = bits * 4
        pct = 100.0 * per_page_agree[pi] / mx
        print(f"  P{pi+1:02d}     {bits:<8} {per_page_agree[pi]:<14} {mx:<10} {pct:>6.2f}%")
    overall_pct = 100.0 * total_agreements / max_possible
    print(f"\n  Overall torus agreement: {total_agreements}/{max_possible} = {overall_pct:.2f}%")

    # 4c — Torus wrap-around XOR: page 1 ⊕ page 14 (the seam)
    subsection("4c. Torus seam analysis — Page 1 ⊕ Page 14 (the connecting edge)")
    p1 = PAGES_FULL[0]
    p14 = PAGES_FULL[-1]
    seam_xor = xor_bits(p1, p14)
    print(f"  Page 1  ({len(p1):>3} bits):  {p1}")
    print(f"  Page 14 ({len(p14):>3} bits): {p14}")
    print(f"  XOR     ({len(seam_xor):>3} bits): {seam_xor}")
    diffs = count_ones(seam_xor)
    print(f"\n  Seam differences: {diffs} / {len(seam_xor)} bits ({100.0*diffs/len(seam_xor):.2f}%)")
    print(f"  Seam agreements:  {len(seam_xor)-diffs} / {len(seam_xor)} bits ({100.0*(len(seam_xor)-diffs)/len(seam_xor):.2f}%)")

    # 4d — Full torus stream (concatenated cyclically)
    subsection("4d. Full cyclic torus stream — decode as 8-bit ASCII")
    # Flatten all pages, then repeat cycle once (p14 → p1 → ... → p14 → p1)
    flat = "".join(PAGES_FULL)
    cyclic = flat + flat   # one wrap of the torus
    print(f"  Flat stream length:   {len(flat)} bits")
    print(f"  Cyclic stream length: {len(cyclic)} bits (one full torus cycle)\n")
    decoded = bits_to_ascii(flat)
    print(f"  ASCII decode of flat stream ({len(decoded)} chars):")
    for chunk in textwrap.wrap(decoded, 64):
        print(f"    {chunk}")

    # 4e — Page ring statistics
    subsection("4e. Torus ring statistics (page-to-page XOR chain, full ring)")
    total_diff = 0
    total_comp = 0
    print(f"  {'Edge':<16} {'Compared':<12} {'Diffs':<10} {'% diff'}")
    print(f"  {'-'*50}")
    for i in range(NUM_PAGES):
        j = wrap_index(i + 1, NUM_PAGES)
        r = xor_bits(PAGES_FULL[i], PAGES_FULL[j])
        d = count_ones(r)
        total_diff += d
        total_comp += len(r)
        label = f"P{i+1:02d}→P{j+1:02d}"
        print(f"  {label:<16} {len(r):<12} {d:<10} {100.0*d/len(r):.2f}%")
    print(f"\n  Full ring total: {total_diff} differences over {total_comp} compared bits")
    print(f"  Mean edge difference: {100.0*total_diff/total_comp:.2f}%")


# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────────────────────────────────────

def summary():
    section("SUMMARY")
    flat = "".join(PAGES_FULL)
    print(f"  Source:        Simon_Format — 2210_Compilation_Binary_Corrected")
    print(f"  Pages:         {NUM_PAGES} (notebook pages 1–14 of original 16)")
    print(f"  Total bits:    {len(flat)}")
    print(f"  Full words:    {len(flat)//64} × 64-bit words + {len(flat)%64} remainder bits")
    print(f"  Modifications: 1 flipped bit + 5 scaffolding additions (for XOR analysis)")
    print(f"  Overall 1-density: {bit_density(flat):.4f}")
    print()
    print("  Context: This binary was recorded by USAF Sgt. Jim Penniston during")
    print("  the Rendlesham Forest Incident, December 26-27, 1980, RAF Woodbridge, UK.")
    print("  The code famously decodes (when properly aligned) to:")
    print("    'EXPLORATION OF HUMANITY 666 8100'")
    print("    '52.0942532N 13.131269W'")
    print("    'CONTINUOUS FOR PLANETARY ADVANCE THROUGH NORMAL CHANNELS'")


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 78)
    print("  RENDLESHAM FOREST INCIDENT — BINARY CODE ANALYSIS")
    print("  Jim Penniston Notebook Binary (Simon_Format, Corrected)")
    print("=" * 78)
    print(f"  Pages loaded: {NUM_PAGES}  |  Total bits: {sum(len(p) for p in PAGES_FULL)}")

    xor_analysis()
    stacking_analysis()
    analysis_64bit()
    torus_analysis()
    summary()

    print("\n" + "=" * 78)
    print("  Analysis complete.")
    print("=" * 78)
