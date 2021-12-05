const InteractButton = ({ label, message, show_message, color, type, postpone, abort }) => {

/*
label - label of button
message - feedback after click
show_message - hode button and show message (true/false)
postbone - hide from startscreen
abort - shows x-button
type - normal or submit (for forms)
*/

if (type == 'button') {

  if (show_message) {
    return (
      <div className='fc_btn_group'>
      <button className={`fc_btn inactive ${color}`}>{message}</button>
      </div>
    )
  } else {
    return (
      <div className='fc_btn_group'>
      <button className={`fc_btn ${color}`}>{label}</button>
      </div>
    )

  }
}

if (type === 'submit') {

  if (show_message) {
    return (
      <div className='fc_btn_group'>
      <button type="submit" className={`fc_btn inactive ${color}`}>{message}</button>
      </div>
    )
  } else {
    return (
      <div className='fc_btn_group'>
      <button type="submit" className={`fc_btn ${color}`}>{label}</button>
      </div>
    )

  }
}

}

InteractButton.defaultProps = {
  color: 'green',
  type: 'button'
}

export default InteractButton
