
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tool")
    parser.add_argument("-p", "--path", type=str,
                        help="_path_ of target")
    parser.add_argument("-np", "--new_path", type=str,
                        help="new _path_")
    args = parser.parse_args()

    if args.tool == 'grab_temp':
        from arknights.resource.dev import grab_temp
        while True:
            input('press enter to grab')
            grab_temp.grab(save=True)

    elif args.tool == 'grab_pos':
        from arknights.resource.dev import grab_pos
        while True:
            input('press enter to grab')
            grab_pos.grab(save=True)

    elif args.tool == 'grab_rect':
        from arknights.resource.dev import grab_rect
        while True:
            input('press enter to grab')
            grab_rect.grab(save=True)

    elif args.tool == 'loc_temp':
        from arknights.resource.dev import grab_temp
        while True:
            input('press enter to localize')
            grab_temp.grab(save=False)

    elif args.tool == 'loc_pos':
        from arknights.resource.dev import grab_pos
        while True:
            input('press enter to localize')
            grab_pos.grab(save=False)

    elif args.tool == 'loc_rect':
        from arknights.resource.dev import grab_rect
        while True:
            input('press enter to localize')
            grab_rect.grab(save=False)

    elif args.tool == 'ls_temp':
        from arknights.resource.dev import list_temp
        list_temp.ls()

    elif args.tool == 'ls_pos':
        from arknights.resource.dev import list_pos
        list_pos.ls()

    elif args.tool == 'ls_rect':
        from arknights.resource.dev import list_rect
        list_rect.ls()

    elif args.tool == 'del_temp':
        if args.path is not None:
            from arknights.resource.dev import delete_temp
            delete_temp.delete(args.path)
        else:
            print('must specific target\'s path')

    elif args.tool == 'del_pos':
        if args.path is not None:
            from arknights.resource.dev import delete_pos
            delete_pos.delete(args.path)
        else:
            print('must specific target\'s path')

    elif args.tool == 'del_rect':
        if args.path is not None:
            from arknights.resource.dev import delete_rect
            delete_rect.delete(args.path)
        else:
            print('must specific target\'s path')

    elif args.tool == 'mov_temp':
        if args.path is not None and args.new_path is not None:
            from arknights.resource.dev import move_temp
            move_temp.move(args.path, args.new_path)
        else:
            print('must specific target\'s path')

    elif args.tool == 'mov_pos':
        if args.path is not None and args.new_path is not None:
            from arknights.resource.dev import move_pos
            move_pos.move(args.path, args.new_path)
        else:
            print('must specific target\'s path')

    elif args.tool == 'mov_rect':
        if args.path is not None and args.new_path is not None:
            from arknights.resource.dev import move_rect
            move_rect.move(args.path, args.new_path)
        else:
            print('must specific target\'s path')
