from operating_system import OperatingSystem
import shlex
import os
import random

DISK_FILENAME = "harddisk.txt"
DISK_TOTAL_SIZE_MB = 256
BLOCK_SIZE_KB = 4
INODE_SIZE_KB = 1

INODE_NAME_MAX_LEN = 260
INODE_TIMESTAMP_LEN = 12  # Formato DDMMYYYYHHMM
INODE_SIZE_FIELD_LEN = 10

def fun_and_giggles():
  return random.choice([
      "😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆", "😉", "😊",
      "😋", "😎", "😍", "😘", "😗", "😙", "😚", "🙂", "🤗", "🤔",
      "🤨", "😐", "😑", "😶", "🙄", "😏", "😣", "😥", "😮", "🤐",
      "😯", "😪", "😫", "😴", "😌", "😛", "😜", "😝", "🤤", "😒",
      "😓", "😔", "😕", "🙃", "🤑", "😲", "☹️", "🙁", "😖", "😞",
      "😟", "😤", "😢", "😭", "😦", "😧", "😨", "😩", "🤯", "😬",
      "😰", "😱", "😳", "🤪", "😵", "😡", "😠", "🤬", "😷", "🤒",
      "🤕", "🤢", "🤮", "🤧", "😇", "🤠", "🤡", "🤥", "🤫", "🤭",
      "🧐", "🤓", "👍", "👎", "❤️", "💔", "💯", "🔥", "🎉", "✨",
      "🌟", "🚀", "💡", "💻", "🧠", "👋", "🙏", "🙌", "👏"
  ])

def main():
    print(f'Disk size (mb): {DISK_TOTAL_SIZE_MB}')
    print(f'Block size (kb): {BLOCK_SIZE_KB}')
    print(f'Inode size (kb): {INODE_SIZE_KB}')
    print()

    os_instance = OperatingSystem(
        disk_filename=DISK_FILENAME,
        disk_total_size_mb=DISK_TOTAL_SIZE_MB,
        block_size_kb=BLOCK_SIZE_KB,
        inode_size_kb=INODE_SIZE_KB,
        inode_name_max_len=INODE_NAME_MAX_LEN,
        inode_timestamp_len=INODE_TIMESTAMP_LEN,
        inode_size_field_len=INODE_SIZE_FIELD_LEN
    )
    
    while os_instance.current_user is None:
        name =  input("\nUsuário não logado! Por favor digite seu nome: ")
        os_instance.create_user(name)
        os_instance.login(name)

    # main loop shell
    while True:
        try:
            cwd_path = str(os_instance.file_system.current_directory)
            prompt = (f"{os_instance.current_user.username}@{fun_and_giggles()} "
                      f"~{cwd_path}> ")
            
            command_line = input(prompt)
            if not command_line:
                continue
                
            # Usa shlex para lidar com strings entre aspas (ex: no echo)
            try:
                command_parts = shlex.split(command_line)
            except ValueError as e:
                print(f"Erro ao analisar comando: {e}")
                continue
                
            command = command_parts[0]
            args = command_parts[1:]

            match command:
                case "exit" | "quit" | "sair":
                    os_instance.disk.save_to_disk()
                    break
                case "save":
                    os_instance.disk.save_to_disk()
                    
                case "ls":
                    path = args[0] if args else None
                    path_list = os_instance.parse_path(path) if path else None
                    os_instance.file_system.ls(path_list)
                    
                case "cd":
                    if not args:
                        path_list = os_instance.parse_path("/")
                    else:
                        path_list = os_instance.parse_path(args[0])
                    os_instance.file_system.cd(path_list)
                    
                case "mkdir":
                    if not args: print("mkdir: falta operando")
                    for path_str in args:
                        os_instance.file_system.mkdir(os_instance.parse_path(path_str))
                        
                case "rmdir":
                    if not args: print("rmdir: falta operando")
                    for path_str in args:
                        os_instance.file_system.rmdir(os_instance.parse_path(path_str))
                        
                case "touch":
                    if not args: print("touch: falta operando")
                    for path_str in args:
                        os_instance.file_system.touch(os_instance.parse_path(path_str))
                        
                case "rm":
                    if not args: print("rm: falta operando")
                    for path_str in args:
                        os_instance.file_system.rm(os_instance.parse_path(path_str))
                        
                case "cat":
                    if not args: print("cat: falta operando")
                    for path_str in args:
                        os_instance.file_system.read_file(os_instance.parse_path(path_str))
                        
                case "cp":
                    if len(args) != 2:
                        print("uso: cp <origem> <destino>")
                    else:
                        src_list = os_instance.parse_path(args[0])
                        dest_list = os_instance.parse_path(args[1])
                        os_instance.file_system.cp(src_list, dest_list)
                        
                case "mv":
                    if len(args) != 2:
                        print("uso: mv <origem> <destino>")
                    else:
                        src_list = os_instance.parse_path(args[0])
                        dest_list = os_instance.parse_path(args[1])
                        os_instance.file_system.mv(src_list, dest_list)
                        
                case "ln":
                    if len(args) != 2:
                        print("uso: ln <caminho_alvo> <nome_do_link>")
                    else:
                        target_path_str = args[1]                            
                        link_path_list = os_instance.parse_path(args[2])
                        os_instance.file_system.create_symlink(target_path_str, link_path_list)

                case "stat":
                    if not args: 
                        print("stat: falta operando")
                    else:
                        path_list = os_instance.parse_path(args[0])
                        inode = os_instance.file_system._resolve_path(path_list)
                        
                        if inode:
                            inode.print_metadata()
                        else:
                            print(f"stat: não foi possível obter status de '{args[0]}': Arquivo ou diretório não encontrado")
                
                case "echo":
                    try:
                        operator_index = -1
                        operator = None
                        if ">" in command_parts:
                            operator = ">"
                            operator_index = command_parts.index(">")
                        elif ">>" in command_parts:
                            operator = ">>"
                            operator_index = command_parts.index(">>")
                        
                        if operator is None or operator_index == -1:
                            # Sem redirecionamento, apenas imprime
                            print(" ".join(args))
                            continue
                            
                        content = " ".join(command_parts[1:operator_index])
                        path_str = command_parts[operator_index+1]
                        path_list = os_instance.parse_path(path_str)
                        is_overwrite = (operator == ">")
                        
                        os_instance.file_system.write_to_file(path_list, content, overwrite=is_overwrite)
                        
                    except Exception as e:
                        print(f"echo: Erro ao processar comando: {e}")
                        print('uso: echo "conteudo" > arquivo ou echo "conteudo" >> arquivo')

                case _:
                    print(f"Comando não encontrado: {command}")

        except KeyboardInterrupt:
            print()
            break
        except Exception as e:
            print(f"Um erro inesperado ocorreu: {e}")
            break

    # no final da shell salva tudo no disco, mantendo persistencia meio porca
    os_instance.disk.save_to_disk()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)