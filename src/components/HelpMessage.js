import SVGseparator from './SVGseparator'

const HelpMessage = ({ helpMessage }) => {
  return (
    <section className='help_message_section'>
    <p>{helpMessage}</p>
    <SVGseparator a={60} b={20} c={70} d={40} width={8} />
    </section>
  )
}

export default HelpMessage
