"""``websauna.blog`` workflow.

Module provides a very simple workflow engine for blog posts.
Workflow is designed in pluggable way and can be replaced by using ``IWorkflow``
interface and ``pyramid`` registry.

Motivation. There are a number of good workflows libs around that can be used, so
why creating a new one? Only for development simplicity sake - most of workflow
libs has a large functional overhead and require more complex configuration.
Probably in future this custom workflow will be replaced with one of
existing workflow libs.
"""

# Standard Library
import typing as t
from collections import namedtuple

# Thirdparty Library
from pyramid.security import DENY_ALL
from pyramid.security import Allow
from pyramid.security import Everyone
from zope import interface
from zope.interface.verify import verifyObject

# Websauna
from websauna.system.model.meta import Base

# Websauna's Blog Addon
from websauna.blog.interfaces import IWorkflow


#: ACL permission rule namedtuple
P = namedtuple("Rule", ("permission", "agent", "actions"))


class instance_prop:
    """A marker to make ACL resolving logic to get provided property from a model."""

    def __init__(self, attr: str, prefix: t.Union[None, str] = None) -> None:
        self.attr = attr
        self.prefix = prefix

    def __call__(self, instance: object) -> t.Union[str, None]:
        prop = str(getattr(instance, self.attr, ""))
        if not prop:
            return None
        return self.prefix + prop if self.prefix else prop


class State:
    """Workflow state object.

    Takes a list of ACL.
    """

    def __init__(self, acl: t.Iterable[P]) -> None:
        self.acl = acl


class Transition:
    """Workflow transition, a rule for transiting from one state to another."""

    def __init__(self, from_state: State, to_state: State) -> None:
        self.from_state = from_state
        self.to_state = to_state

    def __call__(self, obj, workflow):
        state = getattr(obj, workflow.state_attr, None)
        state = workflow.states.get(state, workflow.states[workflow.default_state])
        if state is self.to_state:
            return False
        elif state is not self.from_state:
            raise RuntimeError('Transition is not allowed')
        setattr(obj, workflow.state_attr, workflow.reverse_states[self.to_state])
        return True


@interface.implementer(IWorkflow)
class TinyWorkflow:
    """Minimal workflow implementation.

    In this class are defined transactions and transitions in declarative style.
    Additionally this workflow encapsulates ACL resolving.
    """

    #: Model's attribute that contains worflow state.
    state_attr = "state"

    #: Sets of user's permissions mapped to actions.
    permissions = {"viewing": ("view",), "managing": ("view", "edit")}

    #: Public state. Everyone can access object in this state for viewing.
    #: Only owner and admins can perform managing actions.
    public = State(
        acl=(
            P(Allow, Everyone, permissions["viewing"]),
            P(Allow, instance_prop("author_id", prefix="user:"), permissions["managing"]),
            P(Allow, "group:admin", permissions["managing"]),
            P(*DENY_ALL),
        )
    )

    #: Private state. Only owner and admins can perform managing or viewing actions.
    private = State(
        acl=(
            P(Allow, instance_prop("author_id", prefix="user:"), permissions["managing"]),
            P(Allow, "group:admin", permissions["managing"]),
            P(*DENY_ALL),
        )
    )

    #: Post's default state (private).
    default_state = private

    #: Transition to change to object state to public.
    publish_transition = Transition(private, public)

    #: Transition to change to object state to private.
    hide_transition = Transition(public, private)

    def __init__(self, request) -> None:
        self.states = {n: a for n, a in self.__class__.__dict__.items() if isinstance(a, State)}
        self.reverse_states = {v: k for k, v in self.states.items() if k != 'default_state'}
        self.transitions = {n: a for n, a in self.__class__.__dict__.items() if isinstance(a, Transition)}
        for state in self.states:
            setattr(self, state, state)
        self.default_state = self.reverse_states[self.states['default_state']]
        self.states.pop("default_state")

    def transit(self, transition, obj):
        """Perform ``transition`` from one workflow state to another on ``object``."""
        return transition(obj, self)

    def resolve_acl(self, obj: Base) -> t.Iterable[tuple]:
        """Return list of ``object`` ACLs according to its current workflow state."""
        state = getattr(obj, self.state_attr, self.default_state)
        acl = []
        for rule in self.states.get(state, self.states[self.default_state]).acl:
            agent = rule.agent(obj) if isinstance(rule.agent, instance_prop) else rule.agent
            if not agent:
                continue
            acl.append((rule.permission, agent, rule.actions))
        return acl


def get_workflow(request):
    """Get workflow from registry and verify its interface."""
    workflow = request.registry.queryUtility(IWorkflow)
    assert workflow, "No configured IWorkflow"
    verifyObject(IWorkflow, workflow)
    return workflow


def includeme(config):
    """Add ``workflow`` as a method of ``request``."""
    config.add_request_method(get_workflow, name='workflow', reify=True)
