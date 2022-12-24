import {
    ApplicationCommand
} from "discordeno/mod.ts";

export const search: ApplicationCommand = {
    id: 0n,
    applicationId: (Deno.env.get("GAID_APP_ID") as unknown) as bigint,
    name: "",
    description: "",
    dmPermission: false
}