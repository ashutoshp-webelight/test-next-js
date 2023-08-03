from typing import Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi import Depends
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Column, ColumnElement, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import ORMOption

from core.db import Base, db_session
from core.exceptions import InvalidSQLQueryException


Model = TypeVar("Model", bound=Type[Base])
ModelColumn = TypeVar("ModelColumn", bound=Column)
ModelColumnValue = TypeVar("ModelColumnValue", bound=Union[UUID, str, int, bool])

ModelObject = TypeVar("ModelObject", bound=Base)
ModelObjectList = TypeVar("ModelObjectList", bound=List[Base])


class Repository:
    def __init__(self, session: AsyncSession = Depends(db_session)) -> None:
        """
        Call method to inject Repo as a dependency.
        This method also calls a database connection which is injected here.

        :param session: a asynchronous database connection.
        :return: Repo Generator.
        """
        self.session = session

    def save(self, model: Union[ModelObject, ModelObjectList]) -> Union[ModelObject, ModelObjectList]:
        """
        Save the data to the database.

        :param model: A SQLAlchemy model instance.
        :return: A SQLAlchemy model instance.
        """
        if isinstance(model, list):
            self.session.add_all(model)
        else:
            self.session.add(model)
        return model

    async def get(
        self,
        model: Model,
        *args: Optional[ORMOption],
        order_by: Optional[ModelColumn] = None,
        p_key: Optional[Union[UUID, List[UUID]]] = None,
        with_field: Optional[ModelColumn] = None,
        with_field_value: Optional[Union[ModelColumnValue, List[ModelColumnValue]]] = None,
        and_fields: Optional[Dict[ModelColumn, Union[ModelColumnValue, List[ModelColumnValue]]]] = None,
        or_fields: Optional[Dict[ModelColumn, Union[ModelColumnValue, List[ModelColumnValue]]]] = None,
        additional_where_query: Optional[Union[ColumnElement, List[ColumnElement]]] = None,
        return_all: Optional[bool] = False,
        stream_result: Optional[bool] = False,
        page: Optional[bool] = False,
        page_params: Optional[Params] = None,
    ) -> Union[ModelObject, ModelObjectList]:
        """
        Query data from the database.

        This function is universal for all models and for all the query types.\n
        It can be used to query data with primary key, with another field of the table, :class:`and_` and :class:`or_` and to list the table contents, the optional field order_by can be used to order the result when listing.\n  # noqa: E501
        The priority of the query is as follows: Primary key > with_field > and_fields > or_fields.\n
        The function will return the first result if the query is :class:`and_` query or :class:`or_` query and return_first is True.\n  # noqa: E501
        The function will return all results if the query is :class:`and_` query or :class:`or_` query and return_first is True.\n  # noqa: E501
        The function will return a paginated result if page is True and page_params is passed.\n
        The function will return a stream result if stream_result is True. It won't affect the result if page is set to True.\n # noqa: E501

        :param model: Model type.
        :param args: SQLAlchemy options.
        :param order_by: Column by which the result should be ordered.
        :param p_key: Primary key of model the model.
        :param with_field: Column to be query.
        :param with_field_value: Value to be matched.
        :param and_fields: Columns to be mapped.
        :param or_fields: Columns to be mapped.
        :param additional_where_query: Related query to be mapped. Will only be considered if and_fields or or_fields are present. # noqa: E501
        :param return_all: Flag to set the return value to the first result or return all the results.
        :param stream_result: Flag to set the return value to a stream result.
        :param page: Flag to set the return value to a paginated result.
        :param page_params: Pagination parameters.

        :return: A SQLAlchemy model instance.
        :raises InvalidSQLQueryParams: If the query parameters are of invalid combination.
        """
        if page and stream_result:
            raise InvalidSQLQueryException("page and stream_result cannot be True at the same time.")

        if page and not page_params:
            raise InvalidSQLQueryException("page_params should be passed when page is True.")

        query = select(model)
        if args:
            query = query.options(*args)
        if order_by and return_all:
            query = query.order_by(order_by)

        if p_key:
            if isinstance(p_key, list):
                query = query.where(model.id.in_(p_key))
                if page:
                    return await paginate(self.session, query, page_params)
                else:
                    query = await self.session.stream_scalars(query)
                    return await query.all() if not stream_result else query  # type: ignore
            else:
                return (
                    await self.session.get(model, p_key, options=args) if args else await self.session.get(model, p_key)
                )

        elif with_field and with_field_value:
            if additional_where_query:
                query = query.where(
                    *additional_where_query if isinstance(additional_where_query, list) else additional_where_query
                )
            if isinstance(with_field_value, list):
                if not return_all:
                    raise InvalidSQLQueryException(
                        "return_all should be True when querying with a list of values for a single field."
                    )
                query = query.where(with_field.in_(with_field_value))

                if page:
                    return await paginate(self.session, query, page_params)

                query = await self.session.stream_scalars(query)
                return await query.all() if not stream_result else query  # type: ignore

            else:
                query = query.where(with_field == with_field_value)

                if return_all and page:
                    return await paginate(self.session, query, page_params)
                query = await self.session.stream_scalars(query)
                if return_all and not page:
                    return await query.all() if not stream_result else query  # type: ignore
                else:
                    return await query.first() if not stream_result else query

        elif and_fields and not or_fields:
            query = query.where(
                and_(
                    *[
                        field == value if not isinstance(value, (list, tuple)) else field.in_(value)
                        for field, value in and_fields.items()
                    ]
                )
            )
            if additional_where_query is not None:
                query = query.where(
                    *additional_where_query if isinstance(additional_where_query, list) else additional_where_query
                )

            if return_all and page:
                return await paginate(self.session, query, page_params)
            query = await self.session.stream_scalars(query)
            if return_all and not page:
                return await query.all() if not stream_result else query  # type: ignore
            else:
                return await query.first() if not stream_result else query

        elif or_fields and not and_fields:
            query = query.where(
                or_(
                    *[
                        field == value if not isinstance(value, (list, tuple)) else field.in_(value)
                        for field, value in and_fields.items()
                    ]
                )
            )
            if additional_where_query:
                query = query.where(
                    *additional_where_query if isinstance(additional_where_query, list) else additional_where_query
                )

            if return_all and page:
                return await paginate(self.session, query, page_params)
            elif return_all and not page:
                query = await self.session.stream_scalars(query)
                return await query.all() if not stream_result else query  # type: ignore
            else:
                return await query.first() if not stream_result else query

        elif and_fields and or_fields:
            query = query.where(
                and_(
                    *[
                        field == value if not isinstance(value, (list, tuple)) else field.in_(value)
                        for field, value in and_fields.items()
                    ]
                ),
                or_(
                    *[
                        field == value if not isinstance(value, (list, tuple)) else field.in_(value)
                        for field, value in or_fields.items()
                    ]
                ),
            )
            if additional_where_query:
                query = query.where(
                    *additional_where_query if isinstance(additional_where_query, list) else additional_where_query
                )

            if return_all and page:
                return await paginate(self.session, query, page_params)
            elif return_all and not page:
                query = await self.session.stream_scalars(query)
                return await query.all() if not stream_result else query  # type: ignore
            else:
                return await query.first() if not stream_result else query

        else:
            if return_all and page:
                return await paginate(self.session, query, page_params)
            elif return_all and not page:
                query = await self.session.stream_scalars(query)
                return await query.all() if not stream_result else query  # type: ignore
            else:
                return await query.first() if not stream_result else query

    async def delete(self, model: Union[ModelObject, ModelObjectList]) -> None:
        """
        Get data from the database.

        :param model: A SQLAlchemy model instance.
        :return: A SQLAlchemy model instance.
        """
        if isinstance(model, list):
            for _ in model:
                await self.session.delete(_)
        else:
            await self.session.delete(model)
        return None
