from wiki.common.enums import WikiBaseEnum


class ObjectPermissionMode(WikiBaseEnum):
    HIDDEN_INACCESSIBLE = "HIDDEN_INACCESSIBLE"
    INACCESSIBLE = "INACCESSIBLE"
    VIEW_AND_EXPORT = "VIEW_AND_EXPORT"
    # COMMENTING = "COMMENTING"
    # SUGGESTING_CHANGES = "SUGGESTING_CHANGES"
    ABILITY_USE_TEMPLATE = "ABILITY_USE_TEMPLATE"
    EDITING = "EDITING"
    DELETION = "DELETION"


class ObjectPermissionType(WikiBaseEnum):
    GENERAL = "General"
    GROUP = "Group"
    INDIVIDUAL = "Individual"


class ObjectType(WikiBaseEnum):
    WORKSPACE = "Workspace"
    DOCUMENT = "Document"
    BLOCK = "Block"
