import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faArrowRight } from '@fortawesome/free-solid-svg-icons';
import moment from 'moment';

// Custom Toolbar Component
const CustomToolbar = (toolbar) => {
  const goToBack = () => {
    toolbar.onNavigate('PREV');
  };

  const goToNext = () => {
    toolbar.onNavigate('NEXT');
  };

  const goToToday = () => {
    toolbar.onNavigate('TODAY');
  };

  const label = () => {
    const date = moment(toolbar.date);
    return <span>{date.format('MMMM YYYY')}</span>;
  };

  return (
    <div className="custom-toolbar">
      <button onClick={goToBack}>
        <FontAwesomeIcon icon={faArrowLeft} />
      </button>
      <button onClick={goToToday}>Today</button>
      <button onClick={goToNext}>
        <FontAwesomeIcon icon={faArrowRight} />
      </button>
      <div className="current-label">
        {label()}
      </div>
    </div>
  );
};

export default CustomToolbar;
