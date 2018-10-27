import pandas as pd
import logging
logger = logging.getLogger('main.db')

# def create_table(engine, model_list):
#     Obj = model_list[0]
#     Obj.__table__.create(engine)


def bulk_save(session, model_list):
    try:
        session.bulk_save_objects(model_list)
        session.commit()
        # logger.info('Worte to Db.')
    except Exception as e:
        logger.error(e)
        session.rollback()
        pass
