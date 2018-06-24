"""``websauna.blog`` interfaces live here."""
# Thirdparty Library
from zope import interface


class IWorkflow(interface.Interface):
    """``websauna.blog`` wworkflow interface."""

    state_attr = interface.Attribute("""Models workflow attribute name""")
    states = interface.Attribute(
        """Dict of workflow state in format {'state_name': state_instance, ...}""")
    default_state = interface.Attribute("""A default workflow state""")

    def transit(transition, obj):
        """Perform ``transition`` from one workflow state to another on ``object``."""

    def resolve_acl(obj):
        """Return list of ``object`` ACLs according to its current workflow state."""
