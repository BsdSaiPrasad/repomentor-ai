import {
  createUIMessageStream,
  createUIMessageStreamResponse,
  streamText,
  type LanguageModel,
} from "ai";
import { auth } from "@/app/(auth)/auth";
import {
  deleteChatById,
  getChatById,
  getMessagesByChatId,
  saveChat,
  saveMessages,
} from "@/lib/db/queries";
import type { DBMessage } from "@/lib/db/schema";
import { ChatbotError } from "@/lib/errors";
import type { ChatMessage } from "@/lib/types";
import { convertToUIMessages, generateUUID, getTextFromMessage } from "@/lib/utils";
import { type PostRequestBody, postRequestBodySchema } from "./schema";

export const maxDuration = 60;

const backendBaseUrl =
  process.env.REPOMENTOR_API_BASE_URL ?? "http://127.0.0.1:8001";

const mockUsage = {
  inputTokens: { total: 10, noCache: 10, cacheRead: 0, cacheWrite: 0 },
  outputTokens: { total: 20, text: 20, reasoning: 0 },
};

function createStaticTextModel(answer: string): LanguageModel {
  return {
    specificationVersion: "v3",
    provider: "repomentor",
    modelId: "course-assistant",
    defaultObjectGenerationMode: "tool",
    supportedUrls: {},
    doGenerate: async () => ({
      finishReason: "stop",
      usage: mockUsage,
      content: [{ type: "text", text: answer }],
      warnings: [],
    }),
    doStream: async () => ({
      stream: new ReadableStream({
        async start(controller) {
          controller.enqueue({ type: "text-start", id: "t1" });
          for (const word of answer.split(" ")) {
            controller.enqueue({
              type: "text-delta",
              id: "t1",
              delta: `${word} `,
            });
            await new Promise((resolve) => setTimeout(resolve, 8));
          }
          controller.enqueue({ type: "text-end", id: "t1" });
          controller.enqueue({
            type: "finish",
            finishReason: "stop",
            usage: mockUsage,
          });
          controller.close();
        },
      }),
    }),
  } as unknown as LanguageModel;
}

function buildTitleFromMessage(message: ChatMessage) {
  const text = getTextFromMessage(message).trim();
  if (!text) {
    return "New Conversation";
  }
  const words = text.split(/\s+/).slice(0, 5);
  const title = words.join(" ");
  return title.length > 48 ? `${title.slice(0, 45)}...` : title;
}

function toCourseMessages(messages: ChatMessage[]) {
  return messages
    .map((message) => ({
      role: message.role,
      content: getTextFromMessage(message).trim(),
    }))
    .filter((message) => message.content.length > 0);
}

export async function POST(request: Request) {
  let requestBody: PostRequestBody;

  try {
    const json = await request.json();
    requestBody = postRequestBodySchema.parse(json);
  } catch {
    return new ChatbotError("bad_request:api").toResponse();
  }

  try {
    const { id, message, selectedVisibilityType } = requestBody;
    const session = await auth();

    const chat = session?.user ? await getChatById({ id }) : null;
    let messagesFromDb: DBMessage[] = [];
    let title = "New Conversation";

    if (chat) {
      if (!session?.user || chat.userId !== session.user.id) {
        return new ChatbotError("forbidden:chat").toResponse();
      }
      messagesFromDb = await getMessagesByChatId({ id });
      title = chat.title;
    } else if (message?.role === "user" && session?.user) {
      title = buildTitleFromMessage(message as ChatMessage);
      await saveChat({
        id,
        userId: session.user.id,
        title,
        visibility: selectedVisibilityType,
      });
    }

    const uiMessages: ChatMessage[] = [
      ...convertToUIMessages(messagesFromDb),
      ...(message ? [message as ChatMessage] : []),
    ];

    if (message?.role === "user" && session?.user) {
      await saveMessages({
        messages: [
          {
            chatId: id,
            id: message.id,
            role: "user",
            parts: message.parts,
            attachments: [],
            createdAt: new Date(),
          },
        ],
      });
    }

    const backendResponse = await fetch(
      `${backendBaseUrl}/api/v1/course-assistant/chat`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: toCourseMessages(uiMessages),
        }),
      }
    );

    if (!backendResponse.ok) {
      throw new Error("Course assistant backend request failed.");
    }

    const backendResult = await backendResponse.json();
    const answerText =
      typeof backendResult.answer === "string"
        ? backendResult.answer
        : "I couldn't generate an answer from the course materials.";

    const stream = createUIMessageStream({
      execute: async ({ writer: dataStream }) => {
        const result = streamText({
          model: createStaticTextModel(answerText),
          prompt: answerText,
        });

        dataStream.merge(result.toUIMessageStream());
        dataStream.write({ type: "data-chat-title", data: title });
      },
      generateId: generateUUID,
      onFinish: async ({ messages: finishedMessages }) => {
        if (finishedMessages.length > 0 && session?.user) {
          await saveMessages({
            messages: finishedMessages.map((currentMessage) => ({
              id: currentMessage.id,
              role: currentMessage.role,
              parts: currentMessage.parts,
              createdAt: new Date(),
              attachments: [],
              chatId: id,
            })),
          });
        }
      },
      onError: () => {
        return "Sorry, the course assistant could not respond right now.";
      },
    });

    return createUIMessageStreamResponse({ stream });
  } catch (error) {
    console.error("Unhandled error in RepoMentor chat API:", error);
    return new ChatbotError("offline:chat").toResponse();
  }
}

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get("id");

  if (!id) {
    return new ChatbotError("bad_request:api").toResponse();
  }

  const session = await auth();

  if (!session?.user) {
    return new ChatbotError("unauthorized:chat").toResponse();
  }

  const chat = await getChatById({ id });

  if (!chat || chat.userId !== session.user.id) {
    return new ChatbotError("forbidden:chat").toResponse();
  }

  await deleteChatById({ id });

  return Response.json({ ok: true });
}
