import { rest, setApplicationId, upsertSlashCommands } from "./deps.ts";

import { decode } from "encoding/base64url.ts";
import { json } from "sift/mod.ts";

import { commands } from "commands/mod.ts";

export async function redeploy(request: Request) {
    const authorization = request.headers.get("authorization");
    if (
        !authorization || (authorization !== Deno.env.get("REDEPLOY_AUTHORIZATION"))
    ) {
        return json({ error: "Invalid authorization header." }, { status: 401 });
    }

    await updateGlobalCommands();
    return json({ success: true });
}

export async function updateGlobalCommands() {
    const token = Deno.env.get("DISCORD_TOKEN");
    const url = `https://discord.com/api/v10/applications/{appID}/commands`
    rest.token = `Bot ${token}`;
    setApplicationId(
        new TextDecoder().decode(decode(token?.split(".")[0] || "")) || "",
    );

    // UPDATE GLOBAL COMMANDS
    await upsertSlashCommands(
        Object.entries(commands)
            // ONLY GLOBAL COMMANDS
            .filter(([_name, command]) => command?.global).map(
                ([name, command]) => {
                    // const description = `${name.toUpperCase()}_DESCRIPTION`;
    
                    return {
                        name,
                        description: command!.description ||
                            "No description available.",
                        options: command!.options?.map((option) => {
                            const optionName = option.name;
                            const optionDescription = option.description;
                            return {
                                ...option,
                                name: optionName,
                                description: optionDescription || "No description available.",
                            };
                        }),
                    };
                },
            ),
    );
}

export async function updateGuildCommands(guildId: string) {
    // GUILD RELATED COMMANDS
    await upsertSlashCommands(
        Object.entries(commands)
            // ONLY GUILD COMMANDS
            .filter(([_name, command]) => command!.guild !== false).map(
                ([name, command]) => {
                    // USER OPTED TO USE BASIC VERSION ONLY
                    // if (command!.advanced === false) {
                    return {
                        name,
                        description: command!.description || "No description available.",
                        options: command!.options,
                    };
                    // }
  
                    // ADVANCED VERSION WILL ALLOW TRANSLATION
                    // const translatedName = `${name.toUpperCase()}_NAME`;
                    // const translatedDescription = `${name.toUpperCase()}_DESCRIPTION`;
  
                    // return {
                    //     name: name,
                    //     description: command!.description,
                    //     options: command!.options?.map((option) => {
                    //         const optionName = option.name;
                    //         const optionDescription = option.description;
            
                    //         return {
                    //             ...option,
                    //             name: optionName,
                    //             description: optionDescription || "No description available.",
                    //         };
                    //     }),
                    // };
                },
            ),
    );
}
