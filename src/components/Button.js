const Button = ({ text, color, postpone, abort }) => {
  if (abort) {
    return (
      <div className='fc_btn_group'>
      <button className={`fc_btn ${color}`}>{text}</button>
      <button
        onClick={postpone}
        className='fc_btn_abort'
      >
      &times;
      </button>
      </div>
    )
  } else {
    return (
      <div className='fc_btn_group'>
      <button className={`fc_btn ${color}`}>{text}</button>
      </div>
    )

  }
}

Button.defaultProps = {
  color: ''
}

export default Button
