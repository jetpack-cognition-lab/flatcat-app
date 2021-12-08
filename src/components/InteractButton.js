const InteractButton = ({ label, message, show_message, color, type, postpone, abort, onClick, help }) => {
  /*
  label - label of button
  message - feedback after click
  show_message - hode button and show message (true/false)
  postbone - hide from startscreen
  abort - shows x-button
  type - normal or submit (for forms)
  */
  return (
    <div className='fc_btn_group'>
    <button
      className={`fc_btn ${show_message && 'inactive' }
      ${color}`}
      onClick={onClick}
    >
    {`${show_message ? message : label}`}
    </button>
    </div>
  )
}

InteractButton.defaultProps = {
  color: 'green'
}

export default InteractButton
