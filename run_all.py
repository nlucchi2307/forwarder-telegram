import asyncio
import subprocess

async def main():
    tasks = [
        asyncio.create_task(asyncio.to_thread(subprocess.run, ["python3", "forwarder_eng.py"])),
        asyncio.create_task(asyncio.to_thread(subprocess.run, ["python3", "forwarder_it.py"]))
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
