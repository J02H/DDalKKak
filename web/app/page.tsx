import Image from "next/image";
import { Box, VStack, HStack, Text, Button, Input} from "@ddalkkak/components";

export default function Home() {
  return (
    <Box className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <HStack className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">
        <Image
          className="dark:invert"
          src="/next.svg"
          alt="Next.js logo"
          width={100}
          height={20}
          priority
        />
        <VStack className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
          <Text className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
            딸깍
          </Text>
          <Text className="max-w-md text-lg leading-8 text-zinc-600 dark:text-zinc-400">
            여기서 연습하십쇼
          </Text>
        </VStack>

        </HStack>
      </Box>
  );
}
