from src.config.constants import (COLUMN_NAME_PROJECT, COLUMN_NAME_SQUAD, COLUMN_NAME_SQUAD2,
    COLUMN_NAME_SPRINT, COLUMN_NAME_TYPE, COLUMN_NAME_ID, COLUMN_NAME_CALCULATED_COMPONENTS, COLUMN_NAME_CALCULATED_SPRINT, COLUMN_NAME_ASSIGNEE_NAME)
from src.utils.sprint_utils import get_sprint_date_range
from src.utils.string_utils import split_string_array
import pandas as pd
import warnings

class JiraDataFilter:
    projects: list[str]
    squads: list[str]
    sprints: list[str]
    ticket_types: list[str]
    ticketIds: list[str]
    components: list[str]
    assignees: list[str]

    def __init__(self, projects: list[str] = None, squads: list[str] = None, sprints: list[str] = None, ticket_types: list[str] = None, ticketIds: list[str] = None, components: list[str] = None, assignees: list[str] = None):
        self.projects = projects
        self.squads = squads
        self.sprints = sprints
        self.ticket_types = ticket_types
        self.ticketIds = ticketIds
        self.components = components
        self.assignees = assignees

class JiraDataFilterResult:
    @property
    def tickets(self) -> pd.DataFrame:
        return self._tickets

    @property
    def projects(self) -> list[str]:
        return self._projects

    @property
    def squads(self) -> list[str]:
        return self._squads

    @property
    def sprints(self) -> list[str]:
        return self._sprints

    @property
    def ticket_types(self) -> list[str]:
        return self._ticket_types

    @property
    def components(self) -> list[str]:
        return self._components

    @property
    def ticketIds(self) -> list[str]:
        return self._ticketIds

    @property
    def assignees(self) -> list[str]:
        return self._assignees

    def __init__(self, tickets: pd.DataFrame = None, projects: list[str] = None, squads: list[str] = None, sprints: list[str] = None, ticket_types: list[str] = None, ticketIds: list[str] = None, components: list[str] = None, assignees: list[str] = None):
        self._tickets = tickets
        self._projects = projects
        self._squads = squads
        self._sprints = sprints
        self._ticket_types = ticket_types
        self._ticketIds = ticketIds
        self._components = components
        self._assignees = assignees

class JiraDataFilterService:
    def __get_squads(self, tickets: pd.DataFrame) -> list[str]:
        squads = []
        if COLUMN_NAME_SQUAD in tickets.columns:
            # Filter out NaN values and convert to list before sorting
            squads.extend([squad for squad in tickets[COLUMN_NAME_SQUAD].unique() if pd.notna(squad)])

        if COLUMN_NAME_SQUAD2 in tickets.columns:
            squads.extend([squad for squad in tickets[COLUMN_NAME_SQUAD2].unique() if pd.notna(squad)])

        return sorted(squads)

    def __get_sprints(self, tickets: pd.DataFrame) -> list[str]:
        # Get unique sprints
        sprint_set = set()
        for sprint_str in tickets[COLUMN_NAME_SPRINT].dropna().unique():
            sprints = split_string_array(sprint_str, '"-"')
            sprint_set.update(sprint.strip() for sprint in sprints)

        # Get sprint end dates and sort sprints by end date descending
        sprint_dates = {}
        for sprint in sprint_set:
            # Get one ticket from this sprint to get its dates
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                sprint_tickets = tickets[tickets[COLUMN_NAME_SPRINT].str.contains(sprint, na=False)]
            if not sprint_tickets.empty:
                sprint_ticket = sprint_tickets.iloc[0]
                # Convert the Series to a DataFrame with a single row
                sprint_ticket_df = sprint_ticket.to_frame().T
                start_date, _ = get_sprint_date_range(sprint_ticket_df, sprint)
                if start_date and not pd.isna(start_date):
                    # Ensure timezone-naive comparison by converting to UTC and removing timezone
                    sprint_dates[sprint] = start_date.tz_localize(None) if start_date.tz else start_date
                else:
                    # Use timezone-naive minimum timestamp
                    sprint_dates[sprint] = pd.Timestamp.min.tz_localize(None)
            else:
                # If no tickets found for this sprint, use minimum timestamp
                sprint_dates[sprint] = pd.Timestamp.min.tz_localize(None)

        # Sort sprints by start date descending
        return sorted(sprint_dates.keys(), key=lambda x: sprint_dates[x], reverse=True)

    def __get_ticket_types(self, tickets: pd.DataFrame) -> list[str]:
        return sorted(tickets[COLUMN_NAME_TYPE].unique())

    def __get_components(self, tickets: pd.DataFrame) -> list[str]:
        # Get all components from the calculated components column
        all_components = []
        for components_str in tickets[COLUMN_NAME_CALCULATED_COMPONENTS].dropna():
            if isinstance(components_str, list):
                for comp in components_str:
                    if pd.notna(comp):
                        # Handle potential hyphenated values in array elements
                        subparts = str(comp).split('-')
                        all_components.extend(part.strip('"').strip("'").strip() for part in subparts if part.strip())

        # Remove duplicates and sort
        return sorted(list(set(all_components)))

    def __get_assignees(self, tickets: pd.DataFrame) -> list[str]:
        # Filter out NaN values and convert to list before sorting
        assignees = [assignee for assignee in tickets[COLUMN_NAME_ASSIGNEE_NAME].unique() if pd.notna(assignee)]
        return sorted(assignees)

    def filter_tickets(self, tickets: pd.DataFrame, filter: JiraDataFilter) -> JiraDataFilterResult:
        # filter by project
        if filter.projects and None not in filter.projects:
            tickets = tickets[tickets[COLUMN_NAME_PROJECT].isin(filter.projects)]

        # filter by squad
        if filter.squads and None not in filter.squads:
            if COLUMN_NAME_SQUAD in tickets.columns and COLUMN_NAME_SQUAD2 in tickets.columns:
                tickets = tickets[tickets[COLUMN_NAME_SQUAD].isin(filter.squads) | tickets[COLUMN_NAME_SQUAD2].isin(filter.squads)]
            elif COLUMN_NAME_SQUAD in tickets.columns:
                tickets = tickets[tickets[COLUMN_NAME_SQUAD].isin(filter.squads)]
            elif COLUMN_NAME_SQUAD2 in tickets.columns:
                tickets = tickets[tickets[COLUMN_NAME_SQUAD2].isin(filter.squads)]

        # filter by sprint
        if filter.sprints and None not in filter.sprints:
            tickets = tickets[tickets[COLUMN_NAME_CALCULATED_SPRINT].apply(
                lambda x: any(sprint in x for sprint in filter.sprints) if isinstance(x, list) else False
            )]

        # filter by types
        if filter.ticket_types and None not in filter.ticket_types:
            tickets = tickets[tickets[COLUMN_NAME_TYPE].isin(filter.ticket_types)]

        # filter by components
        if filter.components and None not in filter.components:
            tickets = tickets[tickets[COLUMN_NAME_CALCULATED_COMPONENTS].apply(
                lambda x: any(comp in x for comp in filter.components) if isinstance(x, list) else False
            )]

        # filter by ticketId
        if filter.ticketIds and None not in filter.ticketIds:
            tickets = tickets[tickets[COLUMN_NAME_ID].isin(filter.ticketIds)]

        # filter by assignee
        if filter.assignees and None not in filter.assignees:
            tickets = tickets[tickets[COLUMN_NAME_ASSIGNEE_NAME].isin(filter.assignees)]

        squads = self.__get_squads(tickets)
        sprints = self.__get_sprints(tickets)
        ticket_types = self.__get_ticket_types(tickets)
        components = self.__get_components(tickets)
        assignees = self.__get_assignees(tickets)

        return JiraDataFilterResult(
            tickets=tickets,
            squads=squads,
            sprints=sprints,
            ticket_types=ticket_types,
            components=components,
            assignees=assignees
        )
