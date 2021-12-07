import SVGseparator from './SVGseparator'

const Message = ({ theMessage, condition }) => {
  if (condition) {
    return (
      <section>
      <h2>Welcome!</h2>
      <p>Please click on the gear and establish an internet connection!</p>
      <SVGseparator a={60} b={20} c={70} d={40} width={8} />
      </section>
    )
  }
}

export default Message
