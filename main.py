import asyncio


from src import MainLogic


async def main():
    value = float(input('Parsing from $: '))
    main_logic = MainLogic(value)
    await main_logic.run()


if __name__ == '__main__':
    asyncio.run(main())
