import { 
    json, 
    serve, 
    validateRequest 
} from "sift/mod.ts";

import {
  Interaction,
  InteractionResponseTypes,
  InteractionTypes,
  verifySignature,
} from "discordeno/mod.ts";
import { camelize } from "camelize/mod.ts";

import { redeploy } from "utils/mod.ts";
import { commands } from "commands/mod.ts"

serve({
  "/": main,
  "/redeploy": redeploy,
});

async function main(request: Request) {
    const { error } = await validateRequest(request, {
        POST: { headers: ["X-Signature-Ed25519", "X-Signature-Timestamp"], },
    });
    if (error) { return json({error: error.message }, {status: error.status }); }

    const publicKey = Deno.env.get("DISCORD_PUBLIC_KEY");
    if (!publicKey) {
        return json({ error: "Missing Discord public key from environment variables.", });
    }
    const signature = request.headers.get("X-Signature-Ed25519")!;
    const timestamp = request.headers.get("X-Signature-Timestamp")!;
    const { body, isValid } = verifySignature({
        publicKey, signature, timestamp, body: await request.text()  });
    if (!isValid) { return json({ error: "Invalid request: could not verify" }, { status: 401 }); }

    const payload = camelize<Interaction>(JSON.parse(body)) as Interaction;
    switch (payload.type) {
        case InteractionTypes.Ping:
            return json({ type: InteractionResponseTypes.Pong });
        case InteractionTypes.ApplicationCommand:
            return handleApplicationCommand();
        default:
            return json({ error: "Bad request" }, { status: 400 });
    }
}

async function handleApplicationCommand(payload: Interaction) {
    if (!payload.data?.name) {
        return json({
            type: InteractionResponseTypes.ChannelMessageWithSource,
            data: { content: "Something went wrong. I was not able to find the command name in the payload sent by Discord.", },
        });
    }

    const command = commands[payload.data.name];
    if (!command) {
        return json({
            type: InteractionResponseTypes.ChannelMessageWithSource,
            data: { content: "Something went wrong. I was not able to find this command.", },
        });
    }

    // Make sure the user has the permission to run this command.
    if (!(await hasPermissionLevel(command, payload))) {
        return json({
            type: InteractionResponseTypes.ChannelMessageWithSource,
            data: { content: "MISSING_PERM_LEVEL" },
        });
    }

    const result = await command.execute(payload);
    if (!isInteractionResponse(result)) {
        await logWebhook(payload).catch(console.error);
        return json({
            data: result,
            type: InteractionResponseTypes.ChannelMessageWithSource,
        });
    }

    // DENO/TS BUG DOESNT LET US SEND A OBJECT WITHOUT THIS OVERRIDE
    return json(result as unknown as { [key: string]: unknown });
}
