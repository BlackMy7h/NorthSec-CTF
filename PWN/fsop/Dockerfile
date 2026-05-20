# Stage 1: build nsjail against the same glibc as the challenge
FROM ubuntu:18.04 AS nsjail-builder

RUN apt-get update && apt-get install -y \
    bison flex g++ gcc git \
    libprotobuf-dev libnl-route-3-dev libprotoc-dev \
    make pkg-config protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth=1 https://github.com/google/nsjail.git /nsjail \
    && cd /nsjail && make -j$(nproc)

# Stage 2: minimal challenge image
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y socat \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=nsjail-builder /nsjail/nsjail /usr/local/bin/nsjail

RUN useradd -m -s /bin/sh ctf

WORKDIR /home/ctf

COPY chall        ./chall
COPY libc.so.6    ./libc.so.6
COPY ld-2.27.so   ./ld-2.27.so
COPY flag.txt     ./flag.txt

RUN chmod +x chall ld-2.27.so && \
    chmod 444 flag.txt && \
    chown root:root flag.txt

EXPOSE 1337

# socat accepts TCP connections; nsjail wraps each exec in its own PID/mount/net namespace
CMD socat TCP-LISTEN:1337,reuseaddr,fork \
    "EXEC:nsjail --mode e --chroot / --user ctf --group ctf \
     --time_limit 120 --max_cpus 1 --rlimit_as 512 \
     --cwd /home/ctf -- /home/ctf/ld-2.27.so /home/ctf/chall,pty,rawer,stderr"
