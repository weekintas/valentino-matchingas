def fullname_to_lithuanian_vocative_case(fullname: str):
    def convert_to_vocative(word):
        if word.endswith("as"):
            return word[:-2] + "ai"
        elif word.endswith("is"):
            return word[:-2] + "i"
        elif word.endswith("ys"):
            return word[:-2] + "y"
        elif word.endswith("ius"):
            return word[:-3] + "iau"
        elif word.endswith("us"):
            return word[:-2] + "au"
        # elif word.endswith("a"):
        #     return word[:-1] + "a"
        # elif word.endswith("e"):
        #     return word[:-1] + "e"
        elif word.endswith("ė"):
            return word[:-1] + "e"
        else:
            return word  # if rule unknown, leave the word the same

    # TODO: Add the daash back

    # changed_fullname = str(fullname)
    # for delimeter in [" ", "-", "–", "—"]:
    #     fullname_parts = changed_fullname.strip().split(delimeter)
    #     changed_fullname = delimeter.join([convert_to_vocative(part) for part in fullname_parts])
    changed_fullname = str(fullname)
    # for delimeter in [" ", "-", "–", "—"]:
    #     fullname_parts = changed_fullname.strip().split(delimeter)
    #     changed_fullname = delimeter.join([convert_to_genitive(part) for part in fullname_parts])

    fullname_parts = changed_fullname.strip().split(" ")
    changed_fullname = " ".join([convert_to_vocative(part) for part in fullname_parts])
    return changed_fullname


def fullname_to_lithuanian_genitive_case(fullname: str):
    def convert_to_genitive(word):
        if word.endswith("as"):
            return word[:-2] + "o"
        elif word.endswith("is"):
            return word[:-2] + "io"
        elif word.endswith("ys"):
            return word[:-2] + "io"
        elif word.endswith("ius"):
            return word[:-3] + "iaus"
        elif word.endswith("us"):
            return word[:-2] + "aus"
        elif word.endswith("a"):
            return word[:-1] + "os"
        elif word.endswith("e"):
            return word[:-1] + "es"
        elif word.endswith("ė"):
            return word[:-1] + "ės"
        else:
            return word  # if rule unknown, leave the word the same

    # TODO: Add the daash back
    changed_fullname = str(fullname)
    # for delimeter in [" ", "-", "–", "—"]:
    #     fullname_parts = changed_fullname.strip().split(delimeter)
    #     changed_fullname = delimeter.join([convert_to_genitive(part) for part in fullname_parts])

    fullname_parts = changed_fullname.strip().split(" ")
    changed_fullname = " ".join([convert_to_genitive(part) for part in fullname_parts])
    return changed_fullname
