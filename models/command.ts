// import {
//     ApplicationCommandOption,
//     ApplicationCommand,
//     Interaction,
//     InteractionResponse,
//     InteractionCallbackData
// } from "discordeno/mod.ts";

// import { PermissionLevels } from "utils/mod.ts";

// export interface Command {
//     /** The permissions levels that are allowed to use this command. */
//     // permissionLevels?:
//     //     | ((payload: Interaction, command: Command) => boolean | Promise<boolean>)
//     //     | (keyof typeof PermissionLevels)[];
//     /** The name of the command. */
//     name: string;
//     /** The Command type */
//     type: CommandType;
//     /** The description of the command. Can be a i18n key if you use advanced version. */
//     description?: string;
//     /** Whether or not this slash command should be enabled right now. Defaults to true. */
//     enabled?: boolean;
//     /** Whether this slash command should be created per guild. Defaults to true. */
//     // guild?: boolean;
//     /** Whether this slash command should be created once globally and allowed in DMs. Defaults to false. */
//     global?: boolean;
//     /** Whether or not to use the Advanced mode. Defaults to true. */
//     advanced?: boolean;
//     /** The slash command options for this command. */
//     options?: ApplicationCommandOption[];
//     /** The function that will be called when the command is executed. */
//     execute: (
//         payload: Interaction
//     ) =>
//         | InteractionResponse
//         | InteractionCallbackData
//         | Promise<InteractionResponse | InteractionCallbackData>;
// }

// export abstract class SerializeableCommand implements Command {
//     abstract name: string;
//     abstract type: CommandType;
//     description?: string;
//     options?: ApplicationCommandOption[];

//     abstract execute: (payload: Interaction) => 
//         | InteractionResponse 
//         | InteractionCallbackData 
//         | Promise<InteractionResponse | InteractionCallbackData>;

//     registereableObject(): string{
//         let obj : Command = {
//             name: this.name,
//             type: this.type,
            
//         }
//         // deno-lint-ignore no-prototype-builtins
//         if (this.hasOwnProperty('description')) {
//             obj.description = this.description;
//         }
        
//         if (this.hasOwnProperty('options')) {
//             obj.options = [];
//             for (let option in this.options) {
                
//             }
//         }
//     }
// }

export enum CommandType {
    CHAT_INPUT = 1,
    USER,
    MESSAGE
}